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
from .qt import QtGui
from .qt_server import QtServer


class HTMLWidget(QtGui.QWidget):
    """ A Qt based HTML widget to render the jigna template with a given
    domain model context. """

    def __init__(
        self, parent=None, window_flags=0, template=None, context=None
    ):
        super(HTMLWidget, self).__init__(parent, window_flags)

        self.context = context
        self.template = template

        self.webview = self._create()

        # Set the layout
        self.setLayout(QtGui.QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(self.webview)
        self.resize(*template.recommended_size)

    def execute_js(self, js):
        """ Execute the given js string on the HTML widget.
        """
        return self.webview.execute_js(js)

    def show(self):
        """ Reimplemented to always show the widget on front.
        """
        super(HTMLWidget, self).show()

        self.raise_()

    #### Private protocol #####################################################

    def _create(self):
        """ Create the jigna widget to render the template with the context.
        """

        # Set up the server to serve the domain models in context
        server = QtServer(
            base_url = join(os.getcwd(), self.template.base_url),
            html     = self.template.html,
            context  = self.context
        )

        return server.webview