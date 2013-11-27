#
# Enthought product code
#
# (C) Copyright 2013 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is confidential and NOT open source.  Do not distribute.
#

# Standard library.
import inspect
import json
import os
import sys

# Enthought library.
from traits.api import (
    Any, Dict, HasTraits, Instance, Str,
    TraitDictEvent, TraitListEvent
)

# Jigna libary.
from jigna.core.html_widget import HTMLWidget
from jigna.server import Bridge, Server

class QtBridge(Bridge):
    """ QtBridge that handles the client-server communication. """

    #### 'Bridge' protocol ####################################################

    #: The server that we provide the bridge for.
    server = Any

    def send_event(self, event):
        """ Send an event. """

        jsonized_event = json.dumps(event)

        # This looks weird but this is how we fake an event being 'received'
        # on the client side when using the Qt bridge!
        self.widget.execute_js(
            'jigna.client.bridge.handle_event(%r);' % jsonized_event
        )

        return

    #### 'QtBridge' protocol ############################################

    #: The 'HTMLWidget' that contains the QtWebLit malarky.
    widget = Any


class QtServer(Server):
    """ QtServer that exposes Python objects to JS. """

    #: The HTMLWidget which is going to attach to this server
    #: fixme: Ideally, the callbacks etc should be attached to this widget when 
    #: the client connects to the server. We shouldn't require the server to 
    #: know which client it connects to.
    widget = Instance(HTMLWidget)
    def _widget_changed(self):
        #: the circular reference to the server object is a big smell. 
        #: it looks like we might not even need a bridge.
        self._bridge = QtBridge(widget=self.widget, server=self)
