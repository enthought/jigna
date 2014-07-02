#
# Enthought product code
#
# (C) Copyright 2013 Enthought, Inc., Austin, TX
# All right reserved.
#

""" Web implementations of the Jigna Server and Bridge. """


# Standard library.
import json
from os.path import join, dirname
import traceback

# 3rd party library.
from tornado.websocket import WebSocketHandler
from tornado.web import Application, RequestHandler

# Enthought library.
from traits.api import List, Str, Instance

# Jigna library.
from jigna.server import Bridge, Server


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

    #: The tornado `Application` object which specifies rules about how to handle
    #: different requests etc.
    application = Instance(Application)

    #### 'Server' protocol ####################################################

    def initialize(self):
        """ Initialize the web server. This simply creates the web application
        to serve the Python model.
        """
        settings = {
            'static_path'       : join(dirname(__file__), 'js', 'dist'),
            'static_url_prefix' : '/jigna/'
        }

        self.application = Application(
            [
                (r"/_jigna_ws", JignaSocket,   dict(bridge=self._bridge, server=self)),
                (r"/_jigna",    GetFromBridge, dict(server=self)),
                (r".*",         MainHandler,   dict(server=self)),
            ],
            **settings
        )

        return

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
        path = self.request.path[1:]
        if not len(path):
            self.write(self.server.html)
        else:
            self.write(open(join(self.server.base_url, path)).read())

        return

class GetFromBridge(RequestHandler):
    def initialize(self, server):
        self.server = server
        return

    def get(self):
        jsonized_request = self.get_argument("data")

        jsonized_response = self.server.handle_request(jsonized_request)
        self.write(jsonized_response)
        return

##### WebSocket handler #######################################################

class JignaSocket(WebSocketHandler):
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
        except:
            traceback.print_exc()
            self.write_message(json.dumps([request_id, '{}']))
        return

    def on_close(self):
        self.bridge.remove_socket(self)
        return

#### EOF ######################################################################
