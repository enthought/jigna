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

# Enthought library.
from pyface.api import GUI
from traits.api import Any, Dict, HasTraits, Instance, Property, Str

# Jigna libary.
from jigna.core.html_widget import HTMLWidget
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
            html     = self.html
        )
        
        widget = HTMLWidget()
        self._server.connect(widget)
        widget.control.show()

        return

    def serve(self, port=8888, **context):
        """ Serve the view of the given context on the given port. """

        from jigna.web_server import WebServer

        self._server = WebServer(
            base_url = self.base_url,
            context  = context,
            html     = self.html,
            port     = port
        )
        self._server.serve()

        return

    #### Private protocol #####################################################

    #: The server that manages the objects shared via the bridge.
    _server = Instance(Server)

#### EOF ######################################################################
