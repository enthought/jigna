#
# Enthought product code
#
# (C) Copyright 2013 Enthought, Inc., Austin, TX
# All right reserved.
#

# Standard Library
import os
from os.path import join

# Tornado Library
from tornado import web


class WebApp(web.Application):
    """ A web based App to serve the jigna template with a given context over
    the web where it can be viewed using a regular web browser. """

    def __init__(self, handlers=None, default_host="", transforms=None,
                 context=None, template=None, **kw):
        super(WebApp, self).__init__(handlers, default_host, transforms, **kw)

        self.context = context
        self.template = template

        self._application = self._create()

    def update_context(self, context={}):
        """
        Dynamically update the context of the serving application. This will add
        the given models but not remove anything.
        """
        self._server.context.update(context)

    #### Private protocol #####################################################

    def _create(self):
        """
        Create the web application serving the given context. Returns the
        tornado application created.
        """

        # Set up the WebServer to serve the domain models in context
        from jigna.web_server import WebServer
        server = WebServer(
            base_url    = join(os.getcwd(), self.template.base_url),
            html        = self.template.html,
            context     = self.context
        )

        return server.application