"""A web socket based Jigna session.
"""

# External imports.
from mako.template import Template
from textwrap import dedent
import json

# Enthought imports.
from traits.api import List, Int, Any, Str

# Local imports.
from jigna.api import PYNAME
from session import Session
import registry

###############################################################################
# WebSession class.
###############################################################################
class WebSession(Session):

    port = Int(8888)

    address = Str

    ######################################
    # Private traits.
    _current_sockets = Any

    _active_sockets = List


    ###########################################################################
    # Public API.
    ###########################################################################
    def add_socket(self, socket):
        """Add a new websocket connection to the session.
        """
        self._active_sockets.append(socket)
        self.update_all_traits(socket)

    def remove_socket(self, socket):
        """Remove websocket connection from the session.
        """
        self._active_sockets.remove(socket)

    def start(self):
        self.create()

    def create(self):
        self._setup()

    def destroy(self):
        registry.clean()

    def set_trait(self, socket, model_id, tname, value):
        if socket in self._current_sockets:
            self._current_sockets.remove(socket)
            return
        model = registry.registry['models'].get(model_id)
        if model:
            value = json.loads(value)
            if value is not None:
                try:
                    self._current_sockets.add(socket)
                    oldval = getattr(model, tname)
                    value = type(oldval)(value)
                    setattr(model, tname, value)
                finally:
                    self._current_sockets.remove(socket)

    def update_all_traits(self, socket):
        """Update the values of the traits for a particular socket.
        """
        models = registry.registry['models']
        for model_id, model in models.iteritems():
            view = registry.registry['views'][model_id]
            for tname in view.visible_traits:
                js = self._get_trait_change_js(model, tname)
                socket.write_message(unicode(js))

    ###########################################################################
    # Protected API.
    ###########################################################################
    def _setup(self):
        # NOTE: Loading the widget html before binding trait change events is
        # necessary since we need atleast one access to view.html and view.js
        # to have them registered in the registry
        html = self.html
        d = registry.registry['models']
        for model_id, model in d.iteritems():
            view = registry.registry['views'][model_id]
            for tname in view.visible_traits:
                self._bind_trait_change_events(model, tname)
            for editor in view.editors:
                editor.setup_session(session=self)

    def _update_web_ui(self, model, tname, new_value):
        traitchange_js = self._get_trait_change_js(model, tname)
        for socket in self._active_sockets:
            if socket not in self._current_sockets:
                self._current_sockets.add(socket)
                socket.write_message(unicode(traitchange_js))

    def _html_default(self):
        template_str = dedent("""
        <html ng-app>
            <head>
                <script type="text/javascript" src="${jquery}"></script>
                <script type="text/javascript" src="${angular}"></script>
                <!--script type="text/javascript" src="${bootstrapjs}"></script-->

                <script type="text/javascript">

                var jigna_ws = new WebSocket("${ws_url}");
                jigna_ws.onmessage = function(evt) {
                    eval(evt.data);
                };
                var ${pyobj} = {set_trait:
                                    function (model_id, tname, value) {
                                    data = {type: "set_trait",
                                            model_id: model_id,
                                            tname: tname,
                                            value: value};
                                    jigna_ws.send(JSON.stringify(data));
                                    }
                                };
                </script>

                <script type="text/javascript">
                    ${jignajs}
                </script>

                <!--link rel="stylesheet" href="${bootstrapcss}"></link-->
                <style>
                    ${jignacss}
                </style>
            </head>
            <body>
                % for view in views:
                    ${view.html}
                % endfor
            </body>
        </html>
            """)
        template = Template(template_str)
        address = 'localhost' if self.address == '' else self.address
        ws_url = 'ws://%s:%d/jigna'%(address, self.port)

        return template.render(views=self.views,
                               jquery=self.resource_url+'js/jquery.min.js',
                               angular=self.resource_url+'js/angular.min.js',
                               bootstrapjs=self.resource_url+'bootstrap/js/bootstrap.min.js',
                               bootstrapcss=self.resource_url+'bootstrap/css/bootstrap.min.css',
                               jignajs=self.js, jignacss=self.css,
                               pyobj=PYNAME,
                               ws_url=ws_url
                               )

    def __current_sockets_default(self):
        return set()

    def _get_resource_url(self):
        return 'http://{0}/static/'.format(self.resource_host)

    def _resource_host_default(self):
        return 'localhost:%d'%self.port


def serve_session(session, port=8888, thread=False, address=''):
    """Serve the given session on a websocket.

    Parameters
    -----------

    session: WebSession: The WebSession instance to serve.
    port: int: Port to serve UI on.
    thread: bool: If True, start the server on a separate thread.
    address: str: Address where we listen.  Defaults to localhost.
    """
    session.port = port
    session.address = address
    from os.path import join, dirname
    from tornado.websocket import WebSocketHandler
    from tornado.web import Application, RequestHandler
    from tornado.ioloop import IOLoop

    ###########################################################################
    class IndexPage(RequestHandler):
        def get(self):
            self.write(session.html)

    ###########################################################################
    class JignaSocket(WebSocketHandler):
        def open(self):
            session.add_socket(self)

        def on_message(self, message):
            data = json.loads(message)
            msg_type = data['type']
            if msg_type == 'set_trait':
                session.set_trait(self, data['model_id'], data['tname'],
                                  data['value'])

        def on_close(self):
            session.remove_socket(self)

    # Setup the application.
    settings = {
    "static_path": join(dirname(__file__), "resources")
    }
    application = Application([
            (r"/", IndexPage),
            (r"/jigna", JignaSocket),
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


def serve(views, port=8888, thread=False, address=''):
    """Serve the given views on a websocket.

    Parameters
    -----------

    views: list(HTMLView) : a list of HTML views to be served on the web.
    port: int: Port to serve UI on.
    thread: bool: If True, start the server on a separate thread.
    address: str: Address where we listen.  Defaults to localhost.
    """
    session = WebSession(port=port, views=views)
    session.start()
    serve_session(session, thread=thread)
