#
# Enthought product code
#
# (C) Copyright 2013 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is confidential and NOT open source.  Do not distribute.
#
""" Qt implementations of the Jigna Server and Bridge. """


# Standard library.
import json

# Enthought library.
from traits.api import Any, Instance

# Jigna libary.
from jigna.core.html_widget import HTMLWidget
from jigna.server import Bridge, Server


class QtBridge(Bridge):
    """ Qt (via QWebkit) bridge implementation. """

    #### 'Bridge' protocol ####################################################

    def send_event(self, event):
        """ Send an event. """

        jsonized_event = json.dumps(event)

        # This looks weird but this is how we fake an event being 'received'
        # on the client side when using the Qt bridge!
        self.widget.execute_js(
            'jigna.client.bridge.handle_event(%r);' % jsonized_event
        )

        return

    #### 'QtBridge' protocol ##################################################

    #: The 'HTMLWidget' that contains the QtWebLit malarky.
    widget = Any


class QtServer(Server):
    """ Qt (via QWebkit) server implementation. """

    #: The HTMLWidget which is going to attach to this server.
    #:
    #: fixme: Ideally, the callbacks etc should be attached to this widget when
    #: the client connects to the server. We shouldn't require the server to
    #: know which client it connects to.
    widget = Instance(HTMLWidget)
    def _widget_changed(self):
        self._bridge = QtBridge(widget=self.widget, server=self)
        return

#### EOF ######################################################################
