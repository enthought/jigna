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
from traits.api import HasTraits, Instance, Dict, Tuple, Int

# Qt Library
from pyface.qt import QtGui

# Tornado Library
from tornado.ioloop import IOLoop
from tornado import web

# Jigna libary.
from jigna.api import Template
from jigna.server import Server

class View(HasTraits):
    """ An abstract class to represent a jigna view. """

    #### 'View' protocol ######################################################

    #: The jigna template object which contains the HTML template and the JS
    #: code to bind it to Python domain models.
    template = Instance(Template)

    #: The context which is used to render the template. This is a dict of
    #: name-object pairs where the name specifies the name used in the template
    #: to refer to an object.
    context = Dict

    def start(self):
        """
        The (usually) blocking call to start the view.
        """
        raise NotImplementedError

    #### Private protocol #####################################################

    #: The server that manages the objects shared via the bridge.
    _server = Instance(Server)

#### 'QtView' #################################################################

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

#### 'WebAppView' #############################################################

class WebAppView(View):
    """ A web based View to serve the jigna template of a given context. """

    #### 'View' protocol ######################################################

    def start(self):
        """
        Create the view's control and start the web server's event loop. This
        is a *blocking* call.
        """
        ioloop = IOLoop.instance()

        self.create_web_app()
        self.web_app.listen(self.port)

        ioloop.start()

    #### 'WebAppView' protocol ################################################

    web_app = Instance(web.Application)

    port = Int(8000)

    def create_web_app(self):
        """ Create the web application serving the given context. Returns the
        tornado application created. """

        # Set up the WebServer to serve the domain models in context
        from jigna.web_server import WebServer
        self._server = WebServer(
            base_url = join(os.getcwd(), self.template.base_url),
            html     = self.template.html,
            context  = self.context
        )
        self._server.initialize()

        self.web_app = self._server.application

        return self.web_app

#### EOF ######################################################################
