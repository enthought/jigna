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

        self.create_application()
        self.application.listen(self.port)

        ioloop.start()

    #### 'WebApp' protocol ####################################################

    #: The tornado web Application object which serves through a web server the
    #: jigna template rendered with the context. Clients connect to this
    #: application to populate their views.
    application = Instance(web.Application)

    #: Port at which the web application is to be run.
    port = Int(8000)

    def create_application(self):
        """
        Create the web application serving the given context. Returns the
        tornado application created.
        """

        # Set up the WebServer to serve the domain models in context
        from jigna.web_server import WebServer
        self._server = WebServer(
            base_url = join(os.getcwd(), self.template.base_url),
            html     = self.template.html,
            context  = self.context
        )
        self._server.initialize()

        self.application = self._server.application

        return self.application

    def update_context(self, context={}):
        """
        Dynamically update the context of the serving application. This will add
        the given models but not remove anything.
        """
        self._server.context.update(context)
