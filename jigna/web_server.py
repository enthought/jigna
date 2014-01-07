#
# Enthought product code
#
# (C) Copyright 2013 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is confidential and NOT open source.  Do not distribute.
#
""" Web implementations of the Jigna Server and Bridge. """


# Standard library.
import json
from os.path import join, dirname
import traceback

# 3rd party library.
from tornado.ioloop import IOLoop
from tornado.websocket import WebSocketHandler
from tornado.web import Application, RequestHandler

# Enthought library.
from traits.api import List, Str, Int, Instance

# Jigna library.
from jigna.server import Bridge, Server


class WebBridge(Bridge):
    """ Bridge that handles the client-server communication. """

    #### 'Bridge' protocol ####################################################

    def send_event(self, event):
        """ Send an event. """

        try:
            jsonized_event = json.dumps(event)
            message_id = -1
            self.send_data(json.dumps([message_id, jsonized_event]))
        except:
            traceback.print_exc()

        return

    #### 'WebBridge' protocol #################################################

    def send_data(self, data):
        for socket in self._active_sockets:
            socket.write_message(data)

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

    #: Port to serve the UI on.
    #:
    #: Default to 8888.
    port = Int(8888)

    #: Address where we listen.  Defaults to localhost.
    address = Str

    #### 'Server' protocol ####################################################

    def serve(self):
        """ Start the server.

        This is a *blocking* call.

        """
        application = self._create_application()
        application.listen(self.port, address=self.address)

        ioloop = IOLoop.instance()
        ioloop.start()

        return

    #: The trait change dispatch mechanism to use when traits change.
    trait_change_dispatch = Str('same')

    #### Private protocol #####################################################

    _bridge = Instance(WebBridge)
    def __bridge_default(self):
        return WebBridge()

    def _create_application(self):
        """ Create the Web Application. """

        settings = {
            'static_path'       : join(dirname(__file__), 'resources'),
            'static_url_prefix' : '/jigna/'
        }

        application = Application(
            [
                (r"/_jigna_ws", JignaSocket,   dict(bridge=self._bridge, server=self)),
                (r"/_jigna",    GetFromBridge, dict(server=self)),
                (r".*",         MainHandler,   dict(server=self)),
            ],
            **settings
        )

        return application

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
            msg_id, jsonized_request = json.loads(message)
            #print "server got message", msg_id, jsonized_request
            jsonized_response = self.server.handle_request(jsonized_request)
            self.bridge.send_data(json.dumps([msg_id, jsonized_response]))
        except:
            traceback.print_exc()
            self.bridge.send_data(json.dumps([msg_id, '{}']))
        return

    def on_close(self):
        self.bridge.remove_socket(self)
        return

#### EOF ######################################################################
