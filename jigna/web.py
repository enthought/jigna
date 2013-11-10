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
from traits.api import List, Str

# Jigna library.
from jigna_view import Bridge, Broker, DOCUMENT_HTML_TEMPLATE, JignaView


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


class JignaWebView(JignaView):
    """ A factory for HTML/AngularJS based user interfaces on the web. """

    #### 'JignaView' protocol #################################################

    def _get_control(self):
        return None


    def show(self, **context):
        """ Create and show a view of the given context. """

        self._resolve_context_ids(context)
        self._broker.register_objects(context.values())
        self._serve(thread=True)

    #### Private protocol #####################################################

    def __broker_default(self):
        return Broker(bridge=WebBridge(), context=self._context)

    def _html_default(self):
        """ Get the default HTML document for the given model. """

        html     = DOCUMENT_HTML_TEMPLATE.format(
            body_html  = self.body_html,
            head_html  = self.head_html
        )

        return html

    def _serve(self, port=8888, thread=False, address=''):
        """ Serve the given JignaWebView on a websocket.

        Parameters
        -----------

        int port: Port to serve UI on.
        Bool thread: If True, start the server on a separate thread.
        str address: Address where we listen.  Defaults to localhost.

        """

        from tornado.ioloop import IOLoop
        bridge = self._broker.bridge

        # Setup the application.
        settings = {'static_path': join(dirname(__file__), 'resources'),
                    'static_url_prefix': '/jigna/'}

        application = Application(
            [
                (r"/_jigna_ws", JignaSocket, dict(bridge=bridge)),
                (r"/_jigna", GetFromBridge, dict(bridge=bridge)),
                (r".*", MainHandler, dict(jigna_view=self)),
            ],
            **settings
        )
        application.listen(port, address=address)

        ioloop = IOLoop.instance()
        if thread:
            from threading import Thread
            t = Thread(target=ioloop.start)
            t.daemon = True
            t.start()
        else:
            ioloop.start()

        return

    def __widget_default(self):
        return None

###############################################################################
class MainHandler(RequestHandler):
    def initialize(self, jigna_view):
        self.jigna_view = jigna_view

    def get(self):
        print self.request.path
        path = self.request.path[1:]
        print path
        if not len(path):
            self.write(self.jigna_view.html)
        else:
            self.write(open(join(self.jigna_view.base_url, path)).read())


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
