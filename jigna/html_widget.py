#
# Enthought product code
#
# (C) Copyright 2013 Enthought, Inc., Austin, TX
# All right reserved.
#

from __future__ import absolute_import

# Standard Library
import os
from os.path import join

# Local Library
from .qt import QtGui, QtCore
from .qt_server import QtServer


class HTMLWidget(QtGui.QGraphicsView):
    """ A Qt based HTML widget to render the jigna template with a given
    domain model context. """

    def __init__(
        self, parent=None, window_flags=0, context=None, template=None
    ):
        super(HTMLWidget, self).__init__(parent, window_flags)

        self.context = context
        self.template = template

        # Set the scene
        scene = QtGui.QGraphicsScene()
        self.webview = self._create_qwebview()
        scene.addItem(self.webview)
        self.setScene(scene)

        # Layout the graphics view
        self.setFrameShape(QtGui.QFrame.NoFrame)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.resize(*template.recommended_size)

    def execute_js(self, js):
        """ Execute the given js string on the HTML widget.
        """
        return self.webview.execute_js(js)

    def resizeEvent(self, event):
        self.webview.resize(event.size())

    #### Private protocol #####################################################

    def _create_qwebview(self):
        """ Create a qwebview to render the template with the context.
        """

        # Set up the server to serve the domain models in context
        server = QtServer(
            base_url = join(os.getcwd(), self.template.base_url),
            html     = self.template.html,
            context  = self.context
        )

        return server.webview