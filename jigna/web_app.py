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
from traits.api import Instance, Int

# Tornado Library
from tornado.ioloop import IOLoop
from tornado import web

# Local Library
from app import App

class WebApp(App):
    """ A web based App to serve the jigna template with a given context over
    the web where it can be viewed using a regular web browser. """

    #### 'App' protocol ######################################################

    def start(self):
        """
        Create the web app to serve jigna and start the web server's event loop.
        This is a *blocking* call.
        """
        ioloop = IOLoop.instance()

        self.create_web_app()
        self.web_app.listen(self.port)

        ioloop.start()

    #### 'WebApp' protocol ####################################################

    #: The tornado web application which serves the jigna application models
    #: through the web server. Clients connect to this application to populate
    #: their views.
    web_app = Instance(web.Application)

    #: Port at which the web application is to be run.
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
