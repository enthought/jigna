#
# Enthought product code
#
# (C) Copyright 2013 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is confidential and NOT open source.  Do not distribute.
#


# Standard library.
import os
from os.path import abspath, dirname, join

# Enthought library.
from pyface.api import GUI
from traits.api import Any, Dict, HasTraits, Instance, Property, Str

# Jigna libary.
from jigna.core.html_widget import HTMLWidget
from jigna.core.wsgi import FileLoader
from jigna.server import Server


#### HTML templates ###########################################################

DOCUMENT_HTML_TEMPLATE = """
<html ng-app='jigna'>
  <head>
    <script type="text/javascript" src="/jigna/js/jquery.min.js"></script>
    <script type="text/javascript" src="/jigna/js/angular.min.js"></script>
    <script type="text/javascript" src="/jigna/js/jigna.js"></script>

    {head_html}

  </head>

  <body>
    {body_html}
  </body>
</html>
"""


class View(HasTraits):
    """ A factory for HTML/AngularJS based user interfaces. """

    ### 'View' class protocol #################################################

    @classmethod
    def from_file(cls, html_file):
        with open(html_file, 'rb') as f:
            html = f.read()

        return cls(html=html)

    #### 'View' protocol ######################################################

    #: The base url for all resources.
    base_url = Str
    def _base_url_default(self):
        return os.getcwd()

    #: The HTML for the *body* of the view's document.
    body_html = Str

    #: The underlying toolkit control that renders HTML.
    control = Property(Any)
    def _get_control(self):
        return self._widget.control

    #: The HTML for the *head* of the view's document.
    head_html = Str

    #: The HTML for the entire document.
    html = Str
    def _html_default(self):
        """ Get the default HTML document for the given model. """

        html = DOCUMENT_HTML_TEMPLATE.format(
            body_html = self.body_html,
            head_html = self.head_html
        )

        return html

    def show(self, **context):
        """ Create and show a view of the given context. """

        from jigna.qt_server import QtServer

        self._server = QtServer(
            base_url = self.base_url,
            context  = context,
            html     = self.html,
            widget   = self._widget
        )

        self.control.loadFinished.connect(self._on_load_finished)
        self._load_html(self.html, self.base_url)
        self.control.show()

        return

    def serve(self, port=8888, **context):
        """ Serve the view of the given context on port 8888. """

        from jigna.web_server import WebServer

        self._server = WebServer(
            html     = self.html,
            base_url = self.base_url,
            context  = context
        )
        self._server.serve()

        return

    #### Private protocol #####################################################

    #: The server that manages the objects shared via the bridge.
    _server = Instance(Server)

    #: The toolkit-specific widget that renders the HTML.
    _widget = Any
    def __widget_default(self):
        return self._create_widget()

    def _create_widget(self):
        """ Create the HTML widget that we use to render the view. """

        root_paths = {
            'jigna': FileLoader(
                root = join(abspath(dirname(__file__)), 'resources')
            )
        }

        widget = HTMLWidget(
            callbacks        = [('handle_request', self._handle_request)],
            python_namespace = 'qt_bridge',
            root_paths       = root_paths,
            open_externally  = True,
            debug            = True
        )
        widget.create()

        return widget

    def _handle_request(self, request):
        """ Handle a request from a client. """

        return self._server._bridge.handle_request(request)

    def _load_html(self, html, base_url):
        """ Load the given HTML into the widget.

        This call blocks until the document had loaded.

        """

        self._load_finished = False

        self._widget.load_html(html, base_url)

        while not self._load_finished:
            GUI.process_events()

        return

    def _on_load_finished(self):
        """ Called when the HTML document has finished loading. """

        self._load_finished = True

        return

#### EOF ######################################################################
