#
# Enthought product code
#
# (C) Copyright 2013 Enthought, Inc., Austin, TX
# All right reserved.
#
""" A Qt based HTML widget to render a jigna UI. """


from __future__ import absolute_import

# Standard library.
import os
from os.path import join

# Local library.
from .qt import QtCore, QtGui
from .qt_server import QtServer


class HTMLWidget(QtGui.QWidget):
    """ A Qt based HTML widget to render a jigna UI. """

    #### 'object' protocol ####################################################
    
    def __init__(
        self, parent=None, window_flags=QtCore.Qt.Widget, context=None,
        template=None, debug=False
    ):
        """ Constructor. """
        
        super(HTMLWidget, self).__init__(parent, window_flags)

        # Private protocol.
        self._context  = context
        self._template = template
        self._debug    = debug
        self._server   = self._create_server()

        # fixme: This has to be a public attribute for testing *only*.
        self.webview   = self._server.webview
        
        # Set the widget layout.
        self.setLayout(QtGui.QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(self._server.webview)
        self.resize(*template.recommended_size)

    def execute_js(self, js):
        """ Execute the given JS string in the HTML widget. """

        return self._server.webview.execute_js(js)

    #### 'QWidget' protocol ###################################################

    def closeEvent(self, event):
        """ Called when there is a request to close the widget. """

        if event.isAccepted():
            self._server.shutdown()

    #### Private protocol #####################################################

    def _create_server(self):
        """ Create a jigna Qt server to serve the domain models. """

        server = QtServer(
            base_url = join(os.getcwd(), self._template.base_url),
            html     = self._template.html,
            context  = self._context,
            debug    = self._debug
        )

        return server
