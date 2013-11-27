#
# Enthought product code
#
# (C) Copyright 2013 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is confidential and NOT open source.  Do not distribute.
#


# Standard library.
import json
from os.path import join, dirname

# 3rd part library.
from tornado.websocket import WebSocketHandler
from tornado.web import Application, RequestHandler

# Enthought library.
from traits.api import List, Str, Int, Bool

# Jigna library.
from jigna_view import Bridge, Server, DOCUMENT_HTML_TEMPLATE, View


class WebBridge(Bridge):
    """ Bridge that handles the client-server communication. """

    #### 'Bridge' protocol ####################################################

    def send_event(self, event):
        """ Send an event. """

        jsonized_event = json.dumps(event)
        for socket in self._active_sockets:
            socket.write_message(jsonized_event)

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
    """ A server to serve HTML/AngularJS based user interfaces on the web. It uses
    web-sockets for making two-way communication"""

    ### 'WebSocketView' protocol ##############################################

    #: Port to serve UI on.
    port = Int(8888)

    #: Address where we listen.  Defaults to localhost.
    address = Str

    #### 'Server' protocol ####################################################

    def serve(self, **context):
        """ Create and show a view of the given context. """

        self._bridge = WebBridge()
        self._serve(thread=True)

    #### Private protocol #####################################################

    def _serve(self, thread):
        """ Serve the given JignaWebView on a websocket.
        """

        from tornado.ioloop import IOLoop

        # Setup the application.
        settings = {'static_path': join(dirname(__file__), 'resources'),
                    'static_url_prefix': '/jigna/'}

        application = Application(
            [
                (r"/_jigna_ws", JignaSocket, dict(bridge=self._bridge)),
                (r"/_jigna", GetFromBridge, dict(bridge=self._bridge)),
                (r".*", MainHandler, dict(server=self)),
            ],
            **settings
        )
        application.listen(self.port, address=self.address)

        ioloop = IOLoop.instance()
        if thread:
            from threading import Thread
            t = Thread(target=ioloop.start)
            t.daemon = True
            t.start()
        else:
            ioloop.start()

        return

##### Request handlers ########################################################

class MainHandler(RequestHandler):
    def initialize(self, server):
        self.server = server

    def get(self):
        print self.request.path
        path = self.request.path[1:]
        print path
        if not len(path):
            self.write(self.server.html)
        else:
            self.write(open(join(self.server.base_url, path)).read())


###############################################################################
class GetFromBridge(RequestHandler):
    def initialize(self, bridge):
        self.bridge = bridge

    def get(self):
        print "Get from bridge"
        jsonized_request = self.get_argument("data")
        jsonized_response = self.bridge.handle_request(jsonized_request)
        self.write(jsonized_response)


###############################################################################
class JignaSocket(WebSocketHandler):
    def initialize(self, bridge):
        self.bridge = bridge

    def open(self):
        print "Opening jigna websocket"
        self.bridge.add_socket(self)

    def on_message(self, message):
        data = json.loads(message)
        print "on_message", data

    def on_close(self):
        print "Closing jigna websocket"
        self.bridge.remove_socket(self)

#### EOF ######################################################################
