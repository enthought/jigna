#
# Enthought product code
#
# (C) Copyright 2013 Enthought, Inc., Austin, TX
# All right reserved.
#

""" Qt implementations of the Jigna Server and Bridge. """


# Standard library.
import json
from os.path import abspath, dirname, join

# Enthought library.
from traits.api import Any, Str, Instance
from traits.trait_notifiers import set_ui_handler

# Jigna libary.
from jigna.core.web_view_container import WebViewContainer
from jigna.core.wsgi import FileLoader
from jigna.server import Bridge, Server
from jigna.qt import QtWebKit, QtGui
from jigna.utils.gui import ui_handler

class QtBridge(Bridge):
    """ Qt (via QWebkit) bridge implementation. """

    #### 'Bridge' protocol ####################################################

    def send_event(self, event):
        """ Send an event. """

        try:
            jsonized_event = json.dumps(event)
        except TypeError:
            return

        if self.webview_container is None:
            raise RuntimeError("WebViewContainer does not exist")

        else:
            # This looks weird but this is how we fake an event being 'received'
            # on the client side when using the Qt bridge!
            self.webview_container.execute_js(
                'jigna.client.bridge.handle_event(%r);' % jsonized_event
            )

        return

    #### 'QtBridge' protocol ##################################################

    #: The 'WebViewContainer' that contains the QtWebKit malarky.
    webview_container = Any


class QtServer(Server):
    """ Qt (via QWebkit) server implementation. """

    ### 'QtServer' protocol ##################################################

    #: The `WebViewContainer` object which specifies rules about how to handle
    #: different requests etc.
    webview_container = Instance(WebViewContainer)
    def _webview_container_default(self):
        return WebViewContainer()

    #### 'Server' protocol ####################################################

    def initialize(self):
        """ Initialize the Qt server. This simply configures the widget to serve
        the Python model.
        """
        self._bridge = QtBridge(webview_container=self.webview_container)

        self.webview_container.trait_set(
            root_paths = {
                'jigna': FileLoader(
                    root = join(abspath(dirname(__file__)), 'js', 'dist')
                )
            },
            open_externally = False,
            debug = True,
            callbacks = [('handle_request', self.handle_request)],
            python_namespace = 'qt_bridge'
        )

        # This statement makes sure that when we dispatch traits events on the
        # 'ui' thread, it passes on those events though the Qt layer.
        set_ui_handler(ui_handler)

        return

    #: The trait change dispatch mechanism to use when traits change.
    trait_change_dispatch = Str('ui')

    #### 'QtServer' protocol ##################################################

    def connect(self, webview_container):
        """ Connect the given widget to the server. This includes loading the
        html and also enabling custom widget embedding etc. The widget must be
        created already to use this method.
        """
        webview_container.load_html(self.html, self.base_url)

        # Wait till the page is ready (DOM ready)
        #
        # fixme: this is currently a very performance intensive code and needs
        # to be replaced with something much smarter like:
        # http://doc.qt.digia.com/qq/qq27-responsive-guis.html#waitinginalocaleventloop
        while webview_container.loading:
            QtGui.QApplication.processEvents()

        self._enable_qwidget_embedding(webview_container)

    #### Private protocol #####################################################

    _bridge = Instance(QtBridge)

    _plugin_factory = Instance('QtWebPluginFactory')

    def _enable_qwidget_embedding(self, webview_container):
        """ Allow generic qwidgets to be embedded in the generated QWebView.
        """
        global_settings = QtWebKit.QWebSettings.globalSettings()
        global_settings.setAttribute(QtWebKit.QWebSettings.PluginsEnabled, True)

        self._plugin_factory = QtWebPluginFactory(context=self.context)
        webview_container.control.page().setPluginFactory(self._plugin_factory)


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
