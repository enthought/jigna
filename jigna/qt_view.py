#
# Enthought product code
#
# (C) Copyright 2013 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is confidential and NOT open source.  Do not distribute.
#

# Standard Library
import os
from os.path import join

# Enthought Library
from traits.api import Instance, Tuple, Int

# Qt Library
from pyface.qt import QtGui

# Local Library
from view import View

class QtView(View):
    """ A Qt based View to render the jigna template of a given context. """

    #### 'View' protocol ######################################################

    def start(self):
        """
        Create the view's control and start the Qt event loop. This is a
        *blocking* call.
        """
        app = QtGui.QApplication.instance() or QtGui.QApplication([])

        self.create_control()
        self.control.show()

        app.exec_()

    #### 'QtView' protocol ####################################################

    parent = Instance(QtGui.QWidget)

    control = Instance(QtGui.QWidget)

    size = Tuple(Int, Int)
    def _size_default(self):
        return self.template.recommended_size

    def create_control(self):
        """ Create and show the control of the given context. Returns the QWidget
        object created so that various layout operations can be performed on it.
        """

        # Set up the QtServer to serve the domain models in context
        from jigna.qt_server import QtServer
        self._server = QtServer(
            base_url = join(os.getcwd(), self.template.base_url),
            html     = self.template.html,
            context  = self.context
        )
        self._server.initialize()

        # Set up the client
        widget = self._server.widget
        widget.create(parent=self.parent)
        widget.control.resize(self.size[0], self.size[1])

        # Connect the client to the server
        self._server.connect(widget)

        self.control = widget.control

        return self.control
