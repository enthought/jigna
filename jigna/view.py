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
from traits.api import HasTraits, Instance, Dict, Int

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
