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

# Local Library
from .web_server import WebServer, AsyncWebServer


class WebApp(web.Application):
    """ A web based App to serve the jigna template with a given context over
    the web where it can be viewed using a regular web browser. """

    def __init__(self, handlers=None, default_host="", transforms=None,
                 context=None, template=None, trait_change_dispatch="same",
                 async=False, **kw):

        if template is not None:
            template.async = async
        self.context = context
        self.template = template
        self.trait_change_dispatch = trait_change_dispatch
        self.async = async

        if handlers is None:
            handlers = []
        handlers += self._create_handlers()

        super(WebApp, self).__init__(handlers, default_host, transforms, **kw)

    #### Private protocol #####################################################

    def _create_handlers(self):
        """
        Create the web application serving the given context. Returns the
        tornado application created.
        """

        # Set up the WebServer to serve the domain models in context
        klass = AsyncWebServer if self.async else WebServer
        server = klass(
            base_url              = join(os.getcwd(), self.template.base_url),
            html                  = self.template.html,
            context               = self.context,
            trait_change_dispatch = self.trait_change_dispatch
        )

        return server.handlers
