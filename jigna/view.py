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
from os.path import join

# Enthought library.
from traits.api import Bool, HasTraits, Instance, Str, Property, Tuple, Int

# Jigna libary.
from jigna.server import Server


#### HTML templates ###########################################################

DOCUMENT_HTML_TEMPLATE = """
<html ng-app='jigna'>
  <head>
    <script type="text/javascript" src="/jigna/jigna.js"></script>
    <script type="text/javascript">
        jigna.initialize({{async: {async}}});
    </script>

    {head_html}

  </head>

  <body>
    {body_html}
  </body>
</html>
"""


class View(HasTraits):
    """ A factory for HTML/AngularJS based user interfaces. """

    #### 'View' protocol ######################################################

    #: Should we use the async client or not.
    #:
    #: Async client presents a deferred API and is useful when you want to have
    #: your View served over the web where you don't want to freeze the browser
    #: during synchronous GET calls from the server.
    async = Bool(False)

    #: The base url for all resources (relative urls are resolved corresponding
    #: to the current working directory).
    base_url = Str

    #: The HTML for the *body* of the view's document.
    body_html = Str

    #: The HTML for the *head* of the view's document.
    head_html = Str

    #: The file which contains the html
    html_file = Str

    #: The HTML for the entire document.
    #:
    #: The order of precedence in determining its value is:
    #:  1. Directly specified `html` trait
    #:  2. Read the contents of the file specified by the `html_file` trait
    #:  3. Create the jigna template out of specified `body_html` and `head_html`
    #:     traits
    html = Property(Str)
    _html = Str

    #: Size of the widget (in a (width, height) format)
    size = Tuple(Int(600), Int(400))

    def _get_html(self):
        """ Get the default HTML document for the given model. """

        # Return the cached html value if the trait is specified directly
        if len(self._html) > 0:
            return self._html

        # Else, read from the html file if it is specified...
        if len(self.html_file) > 0:
            with open(self.html_file) as f:
                html = f.read()

        # ...otherwise, create the template out of body and head htmls
        else:
            async = 'true' if self.async else 'false'
            html = DOCUMENT_HTML_TEMPLATE.format(
                body_html = self.body_html,
                head_html = self.head_html,
                async     = async,
            )

        return html

    def _set_html(self, html):
        self._html = html

    def create_widget(self, context={}, parent=None, size=None):
        """ Create and show a view of the given context. Returns the QWidget
        object created so that various layout operations can be performed on it.
        """

        # Set up the QtServer to serve the domain models in context
        from jigna.qt_server import QtServer

        self._server = QtServer(
            base_url = join(os.getcwd(), self.base_url),
            context  = context,
            html     = self.html
        )
        self._server.initialize()

        # Connect the client to the server
        widget = self._server.widget
        size = size or self.size
        widget.control.resize(size[0], size[1])
        widget.load_html(self._server.html, self._server.base_url)

        return widget.control

    def create_webapp(self, context={}):
        """ Create the web application serving the given context. Returns the
        tornado application created. """

        # Set up the WebServer to serve the domain models in context
        from jigna.web_server import WebServer

        self._server = WebServer(
            base_url = join(os.getcwd(), self.base_url),
            context  = context,
            html     = self.html,
        )
        self._server.initialize()

        return self._server.application

    #### Private protocol #####################################################

    #: The server that manages the objects shared via the bridge.
    _server = Instance(Server)

#### EOF ######################################################################
