#
# Enthought product code
#
# (C) Copyright 2013 Enthought, Inc., Austin, TX
# All right reserved.
#
""" A Qt based HTML widget to render a jigna UI. """


from __future__ import absolute_import

# Local library.
from jigna.utils.web import get_free_port
from jigna.utils import gui
from .qt import QtCore, QtGui


class WebEngineWidget(QtGui.QWidget):
    """ A QWebEngine based HTML widget to render a jigna UI. """

    #### 'object' protocol ####################################################

    def __init__(
        self, parent=None, window_flags=QtCore.Qt.Widget, context=None,
        template=None, debug=False, async=False,
    ):
        """ Constructor. """

        super(WebEngineWidget, self).__init__(parent, window_flags)

        # Private protocol.
        self._context  = context
        self._template = template
        self._debug    = debug
        self._async    = async
        self._server   = self._create_server()

        # Set the widget layout.
        self.setLayout(QtGui.QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(self.webview)
        self.resize(*template.recommended_size)

    def execute_js(self, js):
        """ Execute the given JS string in the HTML widget. """
        # Wrap the code into a anonymous function call to get results
        js_code = '(function(){%s})()' % js
        js_result = []
        def callback(result):
            js_result.append(result)
        self.browser.page().runJavaScript(js_code, callback)
        while not js_result:
            gui.process_events()
        return js_result[0]

    #### 'QWidget' protocol ###################################################

    def closeEvent(self, event):
        """ Called when there is a request to close the widget. """

        if event.isAccepted():
            from tornado.ioloop import IOLoop
            ioloop = IOLoop.instance()
            ioloop.add_callback(ioloop.stop)

    #### Private protocol #####################################################

    def _create_server(self):
        """ Create a WebApp to serve the domain models. """
        from jigna.web_app import WebApp
        from jigna.qt import QtWebEngine, QtCore

        app = WebApp(
            template = self._template,
            context  = self._context,
            async    = self._async,
        )
        port = get_free_port()
        app.listen(port)

        browser = QtWebEngine.QWebEngineView()
        browser.load(QtCore.QUrl('http://localhost:%d' % port))
        self.webview = browser

        return app
