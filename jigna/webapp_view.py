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
from view import View

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
