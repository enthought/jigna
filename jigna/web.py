import json
from jinja2 import Template
from os.path import join, dirname
from tornado.websocket import WebSocketHandler
from tornado.web import Application, RequestHandler
from traits.api import List, Str

from jigna_view import (Bridge, Broker, DOCUMENT_HTML_TEMPLATE, JignaView)


###############################################################################
class WebBridge(Bridge):

    #### 'Bridge' protocol ####################################################
    def send(self, request):
        """ Send a request to the JS-side. """

        jsonized_request  = json.dumps(request)
        for socket in self._active_sockets:
            socket.write_message(jsonized_request)

    #### 'WebBridge' protocol #################################################
    _active_sockets = List

    def add_socket(self, socket):
        self._active_sockets.append(socket)

    def remove_socket(self, socket):
        self._active_sockets.remove(socket)


###############################################################################
class JignaWebView(JignaView):
    """ A factory for HTML/AngularJS based user interfaces on the web. """

    #### 'JignaView' protocol #################################################

    def _get_control(self):
        return None

    #: The HTML to display.
    html = Str

    def show(self, model):
        """ Create and show a view of the given model. """

        self._broker.register_object(model)
        self.html = self._get_html(model)

        return

    #### Private protocol #####################################################

    def __broker_default(self):
        return Broker(bridge=WebBridge())

    def _get_html(self, model):
        """ Get the HTML document for the given model. """

        template = Template(DOCUMENT_HTML_TEMPLATE)
        html     = template.render(
            jquery     = '/static/js/jquery.min.js',
            angular    = '/static/js/angular.min.js',
            jigna      = '/static/js/jigna.js',
            model_name = 'model',
            id         = id(model),
            body_html  = self.body_html,
            head_html  = self.head_html
        )

        return html

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
        jsonized_response = self.bridge.recv(jsonized_request)
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



###############################################################################
def serve(jigna_view, port=8888, thread=False, address=''):
    """Serve the given JignaWebView on a websocket.

    Parameters
    -----------

    jigna_view: JignaWebView: The JignaView instance to serve.
    port: int: Port to serve UI on.
    thread: bool: If True, start the server on a separate thread.
    address: str: Address where we listen.  Defaults to localhost.
    """
    from tornado.ioloop import IOLoop
    bridge = jigna_view._broker.bridge

    # Setup the application.
    settings = {
    "static_path": join(dirname(__file__), "resources")
    }
    application = Application([
            (r"/_jigna_ws", JignaSocket, dict(bridge=bridge)),
            (r"/_jigna", GetFromBridge, dict(bridge=bridge)),
            (r".*", MainHandler, dict(jigna_view=jigna_view)),
        ], **settings)

    application.listen(port, address=address)
    ioloop = IOLoop.instance()

    if thread:
        from threading import Thread
        t = Thread(target=ioloop.start)
        t.daemon = True
        t.start()
    else:
        ioloop.start()
