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
from .qt import QtGui
from .qt_server import QtServer


class HTMLWidget(QtGui.QWidget):
    """ A Qt based HTML widget to render a jigna UI. """

    #### 'object' protocol #####################################################
    
    def __init__(
        self, parent=None, window_flags=0, context=None, template=None
    ):
        """ Constructor. """
        
        super(HTMLWidget, self).__init__(parent, window_flags)

        # Private protocol.
        self._context  = context
        self._template = template
        self._server   = self._create_server()

        # Set the widget layout.
        self.setLayout(QtGui.QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(self._server.webview)
        self.resize(*template.recommended_size)

    def execute_js(self, js):
        """ Execute the given JS string in the HTML widget. """

        return self._server.webview.execute_js(js)

    #### Private protocol #####################################################

    def _create_server(self):
        """ Create a jigna Qt server to serve the domain models. """

        server = QtServer(
            base_url = join(os.getcwd(), self._template.base_url),
            html     = self._template.html,
            context  = self._context
        )

        return server
