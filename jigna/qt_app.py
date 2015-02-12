#
# Enthought product code
#
# (C) Copyright 2013 Enthought, Inc., Austin, TX
# All right reserved.
#

# Standard Library
import os
from os.path import join

# Enthought Library
from traits.api import Instance

# Qt Library
from pyface.qt import QtGui

# Local Library
from app import App

class QtApp(App):
    """ A Qt based App to render the jigna template with a given context on a
    Qt widget. """

    #### 'App' protocol ######################################################

    def start(self):
        """
        Create the Qt widget to render the template with the context and start
        the Qt event loop. This is a *blocking* call.
        """
        app = QtGui.QApplication.instance() or QtGui.QApplication([])

        self.create_widget()
        self.widget.show()

        app.exec_()

    #### 'QtApp' protocol ####################################################

    #: The QWidget which is also the WebView widget rendering the app's
    #: template with the app's context.
    widget = Instance(QtGui.QWidget)

    def create_widget(self, parent=None):
        """ Create the jigna widget to render the template with the context.
        Return the QWidget object created.
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
        widget.create(parent=parent)
        size = self.template.recommended_size
        widget.control.resize(size[0], size[1])

        # Connect the client to the server
        self._server.connect(widget)

        self.widget = widget.control

        return self.widget

    def execute_js(self, js):
        """ Try to execute the given js string on the client. If the app hasn't
        been started yet, this results in an error.
        """
        return self._server.widget.execute_js(js)
