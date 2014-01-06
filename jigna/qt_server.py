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
from traits.api import Any, Str, Instance
from pyface.qt import QtWebKit

# Jigna libary.
from jigna.server import Bridge, Server

class QtBridge(Bridge):
    """ Qt (via QWebkit) bridge implementation. """

    #### 'Bridge' protocol ####################################################

    def send_event(self, event):
        """ Send an event. """

        jsonized_event = json.dumps(event)

        if self.widget is None:
            raise RuntimeError("Widget does not exist")
        
        else:
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

        self._bridge.widget = widget

        widget.trait_set(
            callbacks = [('handle_request', self.handle_request),
                         ('handle_request_async', self.handle_request_async)],
            python_namespace = 'qt_bridge'
        )

        widget.create()

        self._enable_qwidget_embedding(widget)

        widget.load_html(self.html, self.base_url)

    #### Private protocol #####################################################
    
    _bridge = Instance(QtBridge)
    def __bridge_default(self):
        return QtBridge()

    _factory = Instance('QtWebPluginFactory')

    def _enable_qwidget_embedding(self, widget):
        """ Allow generic qwidgets to be embedded in the generated QWebView.
        """
        global_settings = QtWebKit.QWebSettings.globalSettings()
        global_settings.setAttribute(QtWebKit.QWebSettings.PluginsEnabled, True)

        self._factory = QtWebPluginFactory(context=self.context)
        widget.control.page().setPluginFactory(self._factory)


class QtWebPluginFactory(QtWebKit.QWebPluginFactory):

    MIME_TYPE = 'application/x-qwidget'

    def __init__(self, context):
        self.context = context
        super(self.__class__, self).__init__()

    def plugins(self):
        plugin = QtWebKit.QWebPluginFactory.Plugin()
        plugin.name = 'QWidget'
        mimeType = QtWebKit.QWebPluginFactory.MimeType()
        mimeType.name = self.MIME_TYPE
        plugin.mimeTypes = [mimeType]

        return [plugin]

    def create(self, mimeType, url, argNames, argVals):
        """ Return the QWidget to be embedded.
        """
        if mimeType != self.MIME_TYPE:
            return

        args = dict(zip(argNames, argVals))
        factory = eval(args.get('widget-factory'), self.context)
        
        return factory()

#### EOF ######################################################################
