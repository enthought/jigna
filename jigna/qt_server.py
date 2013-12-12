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
from traits.api import Any, Str

# Jigna libary.
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

    #: The trait change dispatch mechanism to use when traits change.
    trait_change_dispatch = Str('ui')

    def connect(self, widget):
        """ Connect the supplied widget to the server by attaching necessary
        callbacks and loading the html in it.
        """

        self._bridge = QtBridge(widget=widget)

        widget.trait_set(
            callbacks = [('handle_request', self.handle_request),
                         ('handle_request_async', self.handle_request_async)],
            python_namespace = 'qt_bridge'
        )

        widget.create()

        widget.load_html(self.html, self.base_url)

#### EOF ######################################################################
