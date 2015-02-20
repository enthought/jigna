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
from .web_server import WebServer


class WebApp(web.Application):
    """ A web based App to serve the jigna template with a given context over
    the web where it can be viewed using a regular web browser. """

    def __init__(self, handlers=None, default_host="", transforms=None,
                 context=None, template=None, **kw):
        super(WebApp, self).__init__(handlers, default_host, transforms, **kw)

        self.context = context
        self.template = template

        handlers = self._create()
        self.add_handlers('.*$', handlers)

    #### Private protocol #####################################################

    def _create(self):
        """
        Create the web application serving the given context. Returns the
        tornado application created.
        """

        # Set up the WebServer to serve the domain models in context
        server = WebServer(
            base_url    = join(os.getcwd(), self.template.base_url),
            html        = self.template.html,
            context     = self.context
        )

        return server.handlers