#
# Jigna product code
#
# (C) Copyright 2013 Enthought, Inc., Austin, TX
# All right reserved.
#

# Standard library imports.
import logging
from types import NoneType

# Local imports.
from jigna.core.interoperation import create_js_object_wrapper
from jigna.core.network_access import ProxyAccessManager
from jigna.qt import QtCore, QtGui, QtWebKit

logger = logging.getLogger(__name__)


class ProxyQWebView(QtWebKit.QGraphicsWebView):

    DISABLED_ACTIONS = [
        QtWebKit.QWebPage.OpenLinkInNewWindow,
        QtWebKit.QWebPage.DownloadLinkToDisk,
        QtWebKit.QWebPage.OpenImageInNewWindow,
        QtWebKit.QWebPage.OpenFrameInNewWindow,
        QtWebKit.QWebPage.DownloadImageToDisk
    ]

    def __init__(
        self, parent=None, python_namespace=None, callbacks=[], debug=True,
        root_paths={}
    ):
        super(ProxyQWebView, self).__init__(parent)
        self.setPage(ProxyQWebPage())

        # Connect JS with python.
        self.expose_python_namespace(python_namespace, callbacks)

        # Install custom access manager to handle '/jigna' requests.
        access_manager = ProxyAccessManager(root_paths=root_paths)
        self.page().setNetworkAccessManager(access_manager)

        # Disable some actions
        for action in self.DISABLED_ACTIONS:
            self.pageAction(action).setVisible(False)

        # Setup debug flag
        self.page().settings().setAttribute(
            QtWebKit.QWebSettings.DeveloperExtrasEnabled, debug
        )

        # Set sizing policy
        self.setSizePolicy(
            QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding
        )

    def execute_js(self, js):
        """ Execute JavaScript synchronously.

        Warning: under most circumstances, this method should not be called when
        the page is loading.
        """
        frame = self.page().mainFrame()
        result = frame.evaluateJavaScript(js)
        result = self._apply_null_fix(result)

        return result

    def expose_python_namespace(self, python_namespace, callbacks):
        """
        Exposes the given python namespace to Javascript, using which Javascript
        can access the given list of callbacks as if they were methods on the
        object described by the python namespace.

        python_namespace: str:
            Namespace to expose to the JS world. This creates an object of the
            same name and attaches it to window frame.

        callbacks: [method_name: callable]:
            This list of callbacks is what is exposed to the JS world via the
            given python namespace.

        Usage:
        ------

        For example, doing this::

            expose_python_namespace('python', ['say_hello', say_hello])

        will create a window level object on the JS side which looks like this::

            window.python.say_hello == <a function which calls Python land>

        """
        frame = self.page().mainFrame()
        js_wrapper = create_js_object_wrapper(callbacks=callbacks, parent=frame)
        frame.javaScriptWindowObjectCleared.connect(
            lambda: frame.addToJavaScriptWindowObject(
                python_namespace, js_wrapper
            )
        )

    def setHtml(self, html, base_url):
        """ Reimplemented to make sure that when we return, the DOM is ready to
        use.

        Based on the local event loop approach described here:
        http://doc.qt.digia.com/qq/qq27-responsive-guis.html#waitinginalocaleventloop
        """
        event_loop = QtCore.QEventLoop()
        self._loaded = False

        def on_load():
            self._loaded = True
            event_loop.quit()

        self.page().loadFinished.connect(on_load)

        super(ProxyQWebView, self).setHtml(html, base_url)

        if not self._loaded:
            event_loop.exec_()

    #### Private protocol #####################################################

    @staticmethod
    def _apply_null_fix(obj):
        """ Makes sure that None objects coming from Qt bridge are actually None.

        We need this because NoneType objects coming from PyQt are of a
        `QPyNullVariant` type, not None. This method converts such objects to
        the standard None type.
        """
        if isinstance(obj, getattr(QtCore, 'QPyNullVariant', NoneType)):
            return None

        return obj


class ProxyQWebPage(QtWebKit.QWebPage):
    """ Overridden to open external links in a web browser.

    Source: http://www.expobrain.net/2012/03/01/open-urls-in-external-browser-by-javascript-in-webkit/
    """

    def acceptNavigationRequest(self, frame, request, type):
        # Checking this is same as checking if the client side <a> tag making
        # the HTTP request had target="_blank" as an attribute.
        if frame is None:
            import webbrowser
            webbrowser.open_new(request.url().toString())

            return False

        else:
            return super(ProxyQWebPage, self).acceptNavigationRequest(
                frame, request, type
            )

    def createWindow(self, *args, **kwargs):
        return ProxyQWebPage()

if __name__ == '__main__':
    app = QtGui.QApplication([])
    w = ProxyQWebView()
    w.show()
    w.raise_()
    w.load(QtCore.QUrl('http://www.google.com/'))
    app.exec_()
