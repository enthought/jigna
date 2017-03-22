#
# (C) Copyright 2013-2016 Enthought, Inc., Austin, TX
# All right reserved.
#

""" Web implementations of the Jigna Server and Bridge. """


# Standard library.
import json
import mimetypes
from os.path import abspath, dirname, join
import threading
import traceback
try:
    from urllib import unquote
except ImportError:
    # The above import will not work on Python-3.x.
    from urllib.parse import unquote

# 3rd party library.
from tornado.websocket import WebSocketHandler
from tornado.web import Application, RequestHandler, StaticFileHandler
from tornado.ioloop import IOLoop

# Enthought library.
from traits.api import (
    Bool, List, Str, Instance, TraitDictEvent, TraitListEvent
)

# Jigna library.
from jigna.server import Bridge, Server
from jigna.core.wsgi import guess_type

#: Path to jigna.js file
JIGNA_JS_FILE = join(abspath(dirname(__file__)), 'js', 'dist', 'jigna.js')


def normalize_slice(s, size):
    """ Normalize a python slice such that.

    s - slice instance to normalize
    size - the size of original sequence to normalize for

    The returned slice instance has following properties:
      - start, stop, step are all int
      - start < stop
      - step > 1
    """
    start, stop, step = s.indices(size)
    if step < 0:
        step = -step
        start, stop = stop, start
        diff = stop - start
        if diff % step == 0:
            n = diff//step - 1
        else:
            n = diff//step
        start = stop - n*step

        stop += 1

    return slice(start, stop, step)


class WebBridge(Bridge):
    """ Bridge that handles the client-server communication. """

    #### 'Bridge' protocol ####################################################

    def send_event(self, event):
        """ Send an event. """

        # Tornado does not support multiple threads calling send_message.
        # Instead one should add a callback on the IOLoop instance as done
        # below.  See:
        # http://www.tornadoweb.org/en/stable/web.html?highlight=thread#thread-safety-notes

        main_thread = isinstance(
            threading.current_thread(), threading._MainThread
        )

        try:
            jsonized_event = json.dumps(event)
        except TypeError:
            return

        message_id = -1
        data = json.dumps([message_id, jsonized_event])
        for socket in self._active_sockets:
            if main_thread:
                socket.write_message(data)
            else:
                IOLoop.instance().add_callback(socket.write_message, data)

        return

    #### 'WebBridge' protocol #################################################

    def add_socket(self, socket):
        """ Add a client socket. """

        self._active_sockets.append(socket)

        return

    def remove_socket(self, socket):
        """ Remove a client socket. """

        self._active_sockets.remove(socket)

        return

    #### Private protocol #####################################################

    #: All active client sockets.
    _active_sockets = List


class WebServer(Server):
    """ Web-based server implementation.

    This implementation uses web-sockets for making two-way communication.

    """

    ### 'WebServer' protocol ##################################################

    #: The list of tornado handlers which map URL patterns to callables
    handlers = List
    def _handlers_default(self):
        return [
            # To serve jigna.js from package source
            (
                r"/jigna/(.*)", StaticFileHandler,
                dict(path=dirname(JIGNA_JS_FILE))
            ),

            # This handler handles the web socket based async version of the
            # web interface.
            (
                r"/_jigna_ws", AsyncWebSocketHandler,
                dict(bridge=self._bridge, server=self)
            ),

            # This handler handles synchronous GET requests from JS proxy
            # getters and returns the corresponding attribute from the
            # python side.
            (r"/_jigna", SyncGETHandler, dict(server=self)),

            # Main handler which returns the jigna HTML and other resources
            # by resolving it via server's base url.
            (r".*", MainHandler, dict(server=self)),
        ]

    #: The trait change dispatch mechanism to use when traits change.
    trait_change_dispatch = Str('same')

    #### Private protocol #####################################################

    _bridge = Instance(WebBridge)
    def __bridge_default(self):
        return WebBridge()


class AsyncWebServer(WebServer):
    """ Asynchronous Web-based server implementation.

    This implementation uses web-sockets for making two-way communication.
    A GET request is not used in this case.  This allows one to embed
    jigna on another web application.

    """

    def _get_attribute_values(self, obj, attribute_names):
        """ Get the values of all 'public' attributes on an object.

        Return a list of strings.

        """

        return [self._marshal(self._get_attribute_default(obj, name))
                for name in attribute_names]

    def _get_attribute_default(self, obj, name):
        value = getattr(obj, name, None)
        if isinstance(value, list):
            value = []
        elif isinstance(value, dict):
            value = {}
        elif hasattr(value, '__dict__'):
            pass
        elif value is None:
            pass
        else:
            value = type(value)()
        return value

    def _get_dict_info(self, obj):
        """ Get a description of a dict. """
        values = self._get_list_info(list(obj.values()))
        return dict(keys=list(obj.keys()), values=values)

    def _get_instance_info(self, obj):
        """ Get a description of an instance. """

        info = super(WebServer, self)._get_instance_info(obj)

        # If this is a new type, also send the attribute_values.
        if 'attribute_names' in info:
            attribute_values = self._get_attribute_values(
                obj, info['attribute_names']
            )
            info['attribute_values'] = attribute_values
            self._send_new_type_event(info)
            # Now that the type info is sent we do not need to send all that
            # information again.
            info = dict(type_name=info['type_name'])

        return info

    def _get_list_info(self, obj):
        """ Get a description of a list. """
        data = self._marshal_all(obj)
        return dict(length=len(obj), data=data)

    def _send_object_changed_event(self, obj, trait_name, old, new):
        """ Send an object changed event. """

        if trait_name.startswith('_'):
            return

        if isinstance(new, TraitListEvent):
            trait_name  = trait_name[:-len('_items')]
            trait = getattr(obj, trait_name)
            value = id(trait)
            if isinstance(new.index, slice):
                # Handle an extended slice.  Note that one cannot increase the
                # size of the list here.  So one is either deleting elements
                # or changing them.
                added = new.added[0] if len(new.added) > 0 else []
                removed = new.removed[0]
                prev_size = len(trait) + len(removed) - len(added)
                s = normalize_slice(new.index, prev_size)
                if new.index.step < 0:
                    # When the step is negative we swap the order of start and
                    # stop so that start <= stop, we therefore must reverse the
                    # added elements.
                    added = added[::-1]
                info = dict(
                    start=s.start, stop=s.stop, step=s.step,
                    removed=len(removed),
                    added=self._get_list_info(added)
                )
            else:
                # This information can be used by the Array.splice method.
                info = dict(
                    index=new.index, removed=len(new.removed),
                    added=self._get_list_info(new.added)
                )

            data = dict(type='list', value=value, info=info)
            items_event = True

        elif isinstance(new, TraitDictEvent):
            trait_name  = trait_name[:-len('_items')]
            trait = getattr(obj, trait_name)
            value = id(trait)
            added, removed = new.added, list(new.removed.keys())
            for key in new.changed:
                added[key] = trait[key]
            info = dict(removed=removed, added=self._get_dict_info(added))
            data = dict(type='dict', value=value, info=info)
            items_event = True

        else:
            # fixme: intent is non-scalar or maybe container?
            if hasattr(new, '__dict__') or isinstance(new, (dict, list)):
                self._register_object(new)

            data = self._marshal(new)
            items_event = False

        event = dict(
            obj  = str(id(obj)),
            name = trait_name,
            # fixme: This smells a bit, but marshalling the new value gives us
            # a type/value pair which we need on the client side to determine
            # what (if any) proxy we need to create.
            data = data,

            # fixme: This is how we currently detect an 'xxx_items' event on
            # the JS side.
            items_event = items_event
        )

        self.send_event(event)

        return

    def _send_new_type_event(self, data):
        """Send a new_type event.  The data passed is the type information
        dict.
        """
        event = dict(
            obj  = 'jigna',
            name = 'new_type',
            data = data
        )
        self.send_event(event)


##### Request handlers ########################################################


class MainHandler(RequestHandler):

    def initialize(self, server):
        self.server = server

        return

    def get(self):
        path = unquote(self.request.path[1:])
        if not len(path):
            self.write(self.server.html)
        else:
            mime_type, _ = guess_type(path)
            self.set_header('Content-Type', mime_type)
            self.write(open(join(self.server.base_url, path), 'rb').read())

        return


class SyncGETHandler(RequestHandler):

    def data_received(self, chunk):
        pass

    def initialize(self, server):
        self.server = server
        return

    def get(self):
        jsonized_request = self.get_argument("data")

        jsonized_response = self.server.handle_request(jsonized_request)
        self.write(jsonized_response)
        return


class AsyncWebSocketHandler(WebSocketHandler):

    def initialize(self, bridge, server):
        self.bridge = bridge
        self.server = server
        return

    def open(self):
        self.bridge.add_socket(self)
        return

    def on_message(self, message):
        try:
            request_id, jsonized_request = json.loads(message)
            jsonized_response = self.server.handle_request(jsonized_request)
            self.write_message(json.dumps([request_id, jsonized_response]))
        except Exception:
            traceback.print_exc()
            self.write_message(json.dumps([request_id, '{}']))
        return

    def on_close(self):
        self.bridge.remove_socket(self)
        return

    def write_message(self, msg, binary=False):
        return super(AsyncWebSocketHandler, self).write_message(msg, binary)

#### EOF ######################################################################
