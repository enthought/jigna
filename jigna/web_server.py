#
# Enthought product code
#
# (C) Copyright 2013 Enthought, Inc., Austin, TX
# All right reserved.
#

""" Web implementations of the Jigna Server and Bridge. """


# Standard library.
import json
import mimetypes
from os.path import abspath, dirname, join
import traceback
try:
    from urllib import unquote
except ImportError:
    from urllib.parse import unquote

# 3rd party library.
from tornado.websocket import WebSocketHandler
from tornado.web import Application, RequestHandler, StaticFileHandler

# Enthought library.
from traits.api import List, Str, Instance

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
