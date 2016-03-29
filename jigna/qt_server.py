#
# Enthought product code
#
# (C) Copyright 2013 Enthought, Inc., Austin, TX
# All right reserved.
#

""" Qt implementations of the Jigna Server and Bridge. """


# Standard library.
import json
import os
from os.path import abspath, dirname, join

# Enthought library.
from traits.api import Any, Bool, Str, Instance
from traits.trait_notifiers import set_ui_handler

# Jigna library.
from jigna.core.proxy_qwebview import ProxyQWebView
from jigna.core.wsgi import FileLoader
from jigna.server import Bridge, Server
from jigna.qt import QtWebKit
from jigna.utils.gui import ui_handler

#: Path to jigna.js file
JIGNA_JS_FILE = join(abspath(dirname(__file__)), 'js', 'dist', 'jigna.js')
JIGNA_VUE_JS_FILE = join(
    abspath(dirname(__file__)), 'js', 'dist', 'jigna-vue.js'
)


class QtBridge(Bridge):
    """ Qt (via QWebkit) bridge implementation. """

    #### 'Bridge' protocol ####################################################

    def send_event(self, event):
        """ Send an event. """

        try:
            jsonized_event = json.dumps(event)
        except TypeError:
            return

        if self.webview is None:
            raise RuntimeError("WebView does not exist")

        else:
            # This looks weird but this is how we fake an event being
            # 'received' on the client side when using the Qt bridge!
            self.webview.execute_js(
                'jigna.client.bridge.handle_event(%r);' % jsonized_event
            )

        return

    #### 'QtBridge' protocol ##################################################

    #: The 'WebViewContainer' that contains the QtWebKit malarky.
    webview = Any


class QtServer(Server):
    """ Qt (via QWebkit) server implementation. """

    #### 'Server' protocol ####################################################

    def __init__(self, **traits):
        """ Initialize the Qt server.

        This simply configures the widget to serve the Python model.
        
        """

        # This statement makes sure that when we dispatch traits events on the
        # 'ui' thread, it passes on those events through the Qt layer.
        set_ui_handler(ui_handler)

        super(QtServer, self).__init__(**traits)
        self.webview.setUrl(self.home_url)
        self._enable_qwidget_embedding()

        return

    #: Whether to switch on the debug flag or not.
    #:
    #: In debug mode, we show the QtWebkit inspect tools.
    debug = Bool(False)

    #: The trait change dispatch mechanism to use when traits change.
    trait_change_dispatch = Str('ui')

    def shutdown(self):
        """ Shutdown the server.

        Overridden to make sure we close up the QWebView.

        """

        super(QtServer, self).shutdown()

        self.webview.close()

    ### 'QtServer' protocol ##################################################

    #: The `ProxyQWebView` object which specifies rules about how to handle
    #: different requests etc.
    webview = Instance(ProxyQWebView)
    def _webview_default(self):
        user_root, index_file = self.home_url.split('/')[-2:]

        return ProxyQWebView(
            python_namespace = 'qt_bridge',
            callbacks        = [('handle_request', self.handle_request)],
            debug            = self.debug,
            hosts            = {
                user_root: FileLoader(
                    root      = abspath(self.base_url),
                    overrides = {
                        index_file: self.html,
                        join('jigna', 'jigna.js'): open(JIGNA_JS_FILE).read(),
                        join('jigna', 'jigna-vue.js'):
                        open(JIGNA_VUE_JS_FILE).read()
                    }
                ),
                'root.filesystem': FileLoader(root=abspath(os.sep))
            }
        )

    #### Private protocol #####################################################

    _bridge = Instance(QtBridge)
    def __bridge_default(self):
        return QtBridge(webview=self.webview)

    _plugin_factory = Instance('QtWebPluginFactory')

    def _enable_qwidget_embedding(self):
        """ Allow generic qwidgets to be embedded in the generated QWebView.
        """
        global_settings = QtWebKit.QWebSettings.globalSettings()
        global_settings.setAttribute(QtWebKit.QWebSettings.PluginsEnabled,True)

        self._plugin_factory = QtWebPluginFactory(context=self.context)
        self.webview.page().setPluginFactory(self._plugin_factory)


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
        widget_factory = eval(args.get('widget-factory'), self.context)

        return widget_factory()

#### EOF ######################################################################
