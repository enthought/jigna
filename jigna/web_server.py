#
# (C) Copyright 2013-2016 Enthought, Inc., Austin, TX
# All right reserved.
#

""" Web implementations of the Jigna Server and Bridge. """


# Standard library.
import json
import mimetypes
from os.path import abspath, dirname, join
import traceback

# 3rd party library.
from tornado.websocket import WebSocketHandler
from tornado.web import Application, RequestHandler, StaticFileHandler

# Enthought library.
from traits.api import (
    Bool, List, Str, Instance, TraitDictEvent, TraitListEvent
)

# Jigna library.
from jigna.server import Bridge, Server

#: Path to jigna.js file
JIGNA_JS_FILE = join(abspath(dirname(__file__)), 'js', 'dist', 'jigna.js')


class WebBridge(Bridge):
    """ Bridge that handles the client-server communication. """

    #### 'Bridge' protocol ####################################################

    def send_event(self, event):
        """ Send an event. """

        try:
            jsonized_event = json.dumps(event)
        except TypeError:
            return

        message_id = -1
        data = json.dumps([message_id, jsonized_event])
        for socket in self._active_sockets:
            socket.write_message(data)

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

    #: Use async communication, this is useful when the client only
    # communicates via websockets.
    async = Bool(False)

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

    def _get_attribute_values(self, obj, attribute_names):
        """ Get the values of all 'public' attributes on an object.

        Return a list of strings.

        """

        return [self._marshal(self._get_attribute_default(obj, name))
                for name in attribute_names]

    def _get_attribute_default(self, obj, name):
        value = getattr(obj, name)
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
        if self.async:
            values = self._get_list_info(list(obj.values()))
            return dict(keys=list(obj.keys()), values=values)
        else:
            return super(WebServer, self)._get_dict_info(obj)

    def _get_instance_info(self, obj):
        """ Get a description of an instance. """

        info = super(WebServer, self)._get_instance_info(obj)

        if self.async:
            # If this is a new type, also send the attribute_values.
            if 'attribute_names' in info:
                attribute_values = self._get_attribute_values(
                    obj, info['attribute_names']
                )
                info['attribute_values'] = attribute_values

        return info

    def _get_list_info(self, obj):
        """ Get a description of a list. """
        if self.async:
            data = self._marshal_all(obj)
            new_types = {}
            for x in data:
                if x['type'] == 'instance' and len(x['info']) > 1:
                    new_types[x['info']['type_name']] = x['info']

            return dict(length=len(obj), data=data, new_types=new_types)
        else:
            return super(WebServer, self)._get_list_info(obj)

    def _send_object_changed_event(self, obj, trait_name, old, new):
        """ Send an object changed event. """

        if not self.async:
            return super(WebServer, self)._send_object_changed_event(
                obj, trait_name, old, new
            )

        # Otherwise send all the async related info.

        if trait_name.startswith('_'):
            return

        if isinstance(new, TraitListEvent):
            trait_name  = trait_name[:-len('_items')]
            value = id(getattr(obj, trait_name))
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


##### Request handlers ########################################################


class MainHandler(RequestHandler):

    def initialize(self, server):
        self.server = server

        return

    def get(self):
        path = self.request.path[1:]
        if not len(path):
            self.write(self.server.html)
        else:
            mime_type, _ = mimetypes.guess_type(path)
            self.set_header('Content-Type', mime_type)
            self.write(open(join(self.server.base_url, path)).read())

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

#### EOF ######################################################################
