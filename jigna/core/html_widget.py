#
# Jigna product code
#
# (C) Copyright 2013 Enthought, Inc., Austin, TX
# All right reserved.
#

# Standard library imports.
import sys
import webbrowser
import logging
from types import NoneType

# Enthought library imports.
from traits.api import ( HasTraits, Any, Bool, Callable, Dict, Either, Event,
    Instance, List, Property, Str, Tuple, Unicode, implements, on_trait_change,
    Float )

# Local imports.
from jigna.core.i_html_widget import IHTMLWidget
from jigna.core.interoperation import create_js_object_wrapper
from jigna.core.network_access import ProxyAccessManager
from jigna.qt import QtCore, QtGui, QtWebKit, QtNetwork

logger = logging.getLogger(__name__)


class HTMLWidget(HasTraits):
    """ A widget for displaying web content.

    See ``IHTMLWidget`` for detailed documentation.
    """
    implements(IHTMLWidget)

    #### 'IWidget' interface ##################################################

    control = Any

    parent = Any

    #### 'IHTMLWidget' interface ##############################################

    # The URL for the current page. Read only.
    url = Str

    # Whether the page is currently loading.
    loading = Bool(False)

    # Fired when the page has completely loaded.
    loaded = Event

    # The title of the current web page.
    title = Unicode

    # Should links be opened in an external browser? Note that any custom URL
    # handling takes precedence over this option.
    open_externally = Bool(False)

    # The zoom level of the page
    zoom = Property(Float)

    # Additional JavaScript to be executed after the page load finishes.
    post_load_js = List(Str)

    # Whether debugging tools are enabled in the web view.
    debug = Bool(False)

    nav_bar = Bool(True)

    #### Python-JavaScript interoperation #####################################

    # The object to expose to JavaScript using the information below.
    js_object = Instance(HasTraits)

    # A list of callables to expose to Javascript.
    callbacks = List(Either(Str, Tuple(Str, Callable)))

    # A list of traits to expose to Javascript.
    properties = List(Either(Str, Tuple(Str, Str)))

    # The name of the Javascript object that will contain the registered
    # callbacks and properties.
    python_namespace = Str('python')

    # A list of schemes to intercept clicks on and functions to handle them.
    click_schemes = Dict(Str, Callable)

    # A list of hosts and wsgi apps to handle them.
    hosts = Dict(Str, Callable)

    # A list of url root paths and wsgi apps to handle them.
    root_paths = Dict(Str, Callable)

    #### Private interface ####################################################

    _network_access = Any

    # The exposed `PythonContainer` qobjects exposed to javascript in the
    # main frame. This list is maintained to delete the object when
    # it is no longer referenced.
    _exposed_containers = List

    # The disabled actions on the page
    _disabled_actions = List

    ###########################################################################
    # 'IWidget' interface.
    ###########################################################################

    def _create_control(self, parent):
        """ Create and return the toolkit-specific control for the widget.
        """
        # Create control.
        _WebView = WebView if sys.platform == 'darwin' else QtWebKit.QWebView
        control = _WebView(parent)
        control.setSizePolicy(QtGui.QSizePolicy.Expanding,
                              QtGui.QSizePolicy.Expanding)
        page = _WebPage(control)
        page.js_console_msg.connect(self._on_js_console_msg)
        control.setPage(page)
        frame = page.mainFrame()

        # Connect signals.
        frame.javaScriptWindowObjectCleared.connect(self._js_cleared_signal)
        frame.titleChanged.connect(self._title_signal)
        frame.urlChanged.connect(self._url_signal)
        page.navigation_request.connect(self._navigation_request_signal,
                                        QtCore.Qt.DirectConnection)
        page.loadFinished.connect(self._load_finished_signal)

        for action in self._disabled_actions:
            control.pageAction(action).setVisible(False)

        # Install the access manager.
        self._network_access = ProxyAccessManager(root_paths=self.root_paths,
                                                  hosts=self.hosts)
        self._network_access.inject(control)

        if hasattr(self, '_zoom'):
            # _zoom attribute is set by _set_zoom() if zoom property is set
            # before the control is created
            self.zoom = self._zoom
            del self._zoom

        return control

    def destroy(self):
        """ Destroy the control, if it exists.
        """
        # Stop loading and call the page's deleteLater(). Setting the
        # page to None cause crazy crashes and perhaps memory corruption.
        self.control.stop()
        self.control.close()
        self._network_access.deleteLater()
        self.control.page().deleteLater()

        if self.control is not None:
            self.control.hide()
            self.control.deleteLater()
            self.control = None

    ###########################################################################
    # 'IHTMLWidget' interface.
    ###########################################################################

    def create(self, parent=None):
        """ Create the HTML widget's underlying control.
        """
        self.parent = parent
        self.control = self._create_control(parent)

    def execute_js(self, js):
        """ Execute JavaScript synchronously.
        """
        frame = self.control.page().mainFrame()
        result = frame.evaluateJavaScript(js)
        result = self._apply_null_fix(result)

        return result

    def load_html(self, html, base_url=None):
        """ Loads raw HTML into the widget.
        """
        self.loading = True
        if base_url:
            url = base_url
            if not url.endswith('/'):
                url += '/'
            self.control.setHtml(html, QtCore.QUrl.fromLocalFile(url))
        else:
            self.control.setHtml(html)
        self.url = ''

    def load_url(self, url):
        """ Loads the given URL.
        """
        self.loading = True
        self.control.load(QtCore.QUrl(url))
        self.url = url

    #### Navigation ###########################################################

    def back(self):
        """ Navigate backward in history.
        """
        self.control.back()

    def forward(self):
        """ Navigate forward in history.
        """
        self.control.forward()

    def reload(self):
        """ Reload the current web page.
        """
        self.control.reload()

    def stop(self):
        """ Stop loading the curent web page.
        """
        self.control.stop()

    #### Generic GUI methods ##################################################

    def undo(self):
        """ Performs an undo action in the underlying widget.
        """
        self.control.page().triggerAction(QtWebKit.QWebPage.Undo)

    def redo(self):
        """ Performs a redo action in the underlying widget.
        """
        self.control.page().triggerAction(QtWebKit.QWebPage.Redo)

    def cut(self):
        """ Performs a cut action in the underlying widget.
        """
        self.control.page().triggerAction(QtWebKit.QWebPage.Cut)

    def copy(self):
        """ Performs a copy action in the underlying widget.
        """
        self.control.page().triggerAction(QtWebKit.QWebPage.Copy)

    def paste(self):
        """ Performs a paste action in the underlying widget.
        """
        self.control.page().triggerAction(QtWebKit.QWebPage.Paste)

    def select_all(self):
        """ Performs a select all action in the underlying widget.
        """
        self.control.page().triggerAction(QtWebKit.QWebPage.SelectAll)

    ###########################################################################
    # Private interface.
    ###########################################################################

    #### Trait change handlers ################################################

    @on_trait_change('control, debug')
    def _update_debug(self):
        if self.control:
            page = self.control.page()
            page.settings().setAttribute(
                QtWebKit.QWebSettings.DeveloperExtrasEnabled, self.debug)

    @on_trait_change('hosts')
    def _update_network_access(self):
        if self._network_access:
            self._network_access.hosts = self.hosts

    #### Trait property getters/setters #######################################

    def _get_zoom(self):
        if self.control is not None:
            return self.control.zoomFactor()
        else:
            return 1.0

    def _set_zoom(self, zoom):
        if self.control is not None:
            self.control.setZoomFactor(zoom)
        else:
            self._zoom = zoom

    #### Trait initializers ###################################################

    def __disabled_actions_default(self):
        return [QtWebKit.QWebPage.OpenLinkInNewWindow,
                QtWebKit.QWebPage.DownloadLinkToDisk,
                QtWebKit.QWebPage.OpenImageInNewWindow,
                QtWebKit.QWebPage.OpenFrameInNewWindow,
                QtWebKit.QWebPage.DownloadImageToDisk]

    #### Signal handlers ######################################################

    def _js_cleared_signal(self):
        if self.control is not None:
            frame = self.control.page().mainFrame()

            # Since the js `window` object is cleared by the frame which still
            # exists, we need to explicitly delete the exposed objects.
            for exposed_obj in self._exposed_containers:
                exposed_obj.deleteLater()

            self._exposed_containers = exposed_containers = []

            if self.callbacks or self.properties:
                exposed_containers.append(create_js_object_wrapper(
                            self.js_object, self.callbacks, self.properties,
                            parent=frame,
                        ))
                frame.addToJavaScriptWindowObject(
                    self.python_namespace, exposed_containers[-1],
                    )

    def _navigation_request_signal(self, nav_req):
        if self.url == '':
            # If no url has been loaded yet, let the url load.
            return

        qurl = nav_req.request.url()
        str_url = qurl.toString()

        if nav_req.frame is None:
            # request to open in new window.
            # TODO: implement createWindow() to open in a tab.
            # open externally until TODO is completed.
            webbrowser.open_new(str_url)
            nav_req.reject()

        # Now fall back to other handling methods.
        scheme = str(qurl.scheme())
        if scheme in self.click_schemes:
            self.click_schemes[scheme](str_url)
            nav_req.reject()
        elif qurl.host() in self.hosts:
            # Load hosts pages locally even if open_externally is specified.
            return
        elif self.open_externally:
            webbrowser.open_new(str_url)
            nav_req.reject()

    def _load_finished_signal(self, ok):
        # Make sure that the widget has not been destroyed during loading.
        if self.control is not None:
            if ok:
                # Evaluate post-load JS.
                for script in self.post_load_js:
                    self.execute_js(script)

            self.loading = False
            self.loaded = ok

    def _title_signal(self, title):
        self.title = title

    def _url_signal(self, url):
        self.url = url.toString()

    def _on_js_console_msg(self, msg, lineno, sourceid):
        """ Log the javascript console messages. """
        logger.debug('JS: <%s>:%s(%s) %s', self.url, lineno, sourceid, msg)

    def _apply_null_fix(self, obj):
        """ Makes sure that None objects coming from Qt bridge are actually None.

        We need this because NoneType objects coming from PyQt are of a
        `QPyNullVariant` type, not None. This method converts such objects to
        the standard None type.
        """
        if isinstance(obj, getattr(QtCore, 'QPyNullVariant', NoneType)):
            return None

        return obj

    def default_context_menu(self):
        """ Return the default context menu (pyface). """
        if self.control is None:
            return None

        page = self.control.page()
        qmenu = page.createStandardContextMenu()
        return qmenu


class _NavigationRequest(object):
    """ A navigation request object which can be used to indicate whether to
    accept or reject a navigation request in a web page. """
    __slots__ = ['_accepted', 'page', 'frame', 'request', 'type']

    def __init__(self, page, frame, request, type):
        self._accepted = None
        self.page = page
        self.frame = frame
        self.request = request
        self.type = type

    def accept(self):
        """ Indicate that the navigation request must proceed. """
        self._accepted = True

    def reject(self):
        """ Indicate that the navigation request must be cancelled. """
        self._accepted = False

    def ignore(self):
        """ Indicate default behavior for the navigation request. """
        self._accepted = None


class _WebPage(QtWebKit.QWebPage):
    """ QWebpage subclass to enable logging of javascript console messages. """
    js_console_msg = QtCore.Signal(str, int, str)

    # NOTE: This signal's argument is used by the emitter.
    # Use `DirectConnection` when connecting, and connect
    # from objects in same thread.
    navigation_request = QtCore.Signal(_NavigationRequest)

    def __init__(self, parent=None):
        super(_WebPage, self).__init__(parent)

    def supportsExtension(self, extension):
        """ Overridden to enable showing error page (ErrorPageExtension). """
        if extension == self.ErrorPageExtension:
            return True
        else:
            return super(_WebPage, self).supportsExtension(extension)

    def extension(self, extension, option, output):
        """ Overridden to show error page when loading a frame fails. """
        if extension == self.ErrorPageExtension:
            domain_map = {self.QtNetwork: 'Network Error',
                          self.Http: 'HTTP Error',
                          self.WebKit: 'Internal Error'}
            code_type_map = {self.QtNetwork: 'Network Error Code',
                             self.Http: 'HTTP Status Code',
                             self.WebKit: 'Internal Error Code'}
            code_map = {self.QtNetwork:
                            lambda code: QtNetwork.QNetworkReply.NetworkError(code).name,
                        self.Http:
                            lambda code: str(code),
                        self.WebKit:
                            lambda code: str(code)}
            content = '''<html><body>
                         <h1>An error occurred while loading the page.</h1>
                         <h2><b>URL:</b> {url}</h2>
                         <h2><b>Nature of Error:</b> {domain}</h2>
                         <h3><b>{code_type}:</b> {code}</h3>
                         <h3><b>Error Message:</b> {message}</h3>
                         </body></html>'''.format(url=option.url.toString(),
                                domain=domain_map[option.domain],
                                code_type=code_type_map[option.domain],
                                code=code_map[option.domain](option.error),
                                message=option.errorString)
            output.content = bytes(content)
            output.contentType = 'text/html'
            output.encoding = 'UTF-8'
            return True
        return super(_WebPage, self).extension(extension, option, output)

    def javaScriptConsoleMessage(self, message, lineno, source_id):
        self.js_console_msg.emit(message, lineno, source_id)
        return super(_WebPage, self).javaScriptConsoleMessage(
                                                   message, lineno, source_id)

    def acceptNavigationRequest(self, frame, request, type):
        """ Overridden to forward request to navigation handler, if set. """
        nav_req = _NavigationRequest(self, frame, request, type)
        self.navigation_request.emit(nav_req)
        if nav_req._accepted is None:
            return super(_WebPage, self).acceptNavigationRequest(
                                                   frame, request, type)
        else:
            return nav_req._accepted

class WebView(QtWebKit.QWebView):
    """ A QWebView suitable for use in HTMLWidget. """

    def __init__(self, parent):
        super(WebView, self).__init__(parent)
        self.wheel_timer = QtCore.QTimer()
        self.wheel_timer.setSingleShot(True)
        self.wheel_timer.setInterval(25)
        self.wheel_timer.timeout.connect(self._emit_wheel_event)
        self.wheel_accumulator = 0
        self._saved_wheel_event_info = ()

    def fix_key_event(self, event):
        """ Swap Ctrl and Meta on OS X.

        By default, Qt on OS X maps Command to Qt::CTRL and Control to Qt::META
        to make cross-platform keyboard shortcuts convenient. Unfortunataely,
        QWebView adopts this behavior, which makes (for example) jQuery's
        ctrlDown event correspond to Command. This behavior is wrong: on both
        Chrome and Safari, ctrlDown corresponds to Control, not Command.

        NOTE: This is not being used. Kept for posterity in case someone
        can find a way to split the browser page key events from native events.

        NOTE: Swapping is disabled for now: Command key down event for
        Control in browser is more acceptable than changing the Copy/Paste
        shortcuts to be Ctrl+C/Ctrl+V on Mac instead of Cmd+C/Cmd+V,
        which is the cause of a few user bug reports.

        """
        darwin_swapped = not QtCore.QCoreApplication.testAttribute(
            QtCore.Qt.AA_MacDontSwapCtrlAndMeta)

        if darwin_swapped:
            key = event.key()
            if key == QtCore.Qt.Key_Control:
                key = QtCore.Qt.Key_Meta
            elif key == QtCore.Qt.Key_Meta:
                key = QtCore.Qt.Key_Control

            modifiers = event.modifiers() \
                & ~QtCore.Qt.ControlModifier & ~QtCore.Qt.MetaModifier
            if event.modifiers() & QtCore.Qt.ControlModifier:
                modifiers |= QtCore.Qt.MetaModifier
            if event.modifiers() & QtCore.Qt.MetaModifier:
                modifiers |= QtCore.Qt.ControlModifier

            return QtGui.QKeyEvent(event.type(), key, modifiers, event.text(),
                                   event.isAutoRepeat(), event.count())

        return event

    def wheelEvent(self, event):
        """ Reimplemented to work around scrolling bug in Mac.

        Work around https://bugreports.qt-project.org/browse/QTBUG-22269.
        Accumulate wheel events that are within a period of 25ms into a single
        event.  Changes in buttons or modifiers, while a scroll is going on,
        are not handled, since they seem to be too much of a corner case to be
        worth handling.
        """

        self.wheel_accumulator += event.delta()
        self._saved_wheel_event_info = (
                                        event.pos(),
                                        event.globalPos(),
                                        self.wheel_accumulator,
                                        event.buttons(),
                                        event.modifiers(),
                                        event.orientation()
                                    )
        event.setAccepted(True)

        if not self.wheel_timer.isActive():
            self.wheel_timer.start()

    def _emit_wheel_event(self):
        event = QtGui.QWheelEvent(*self._saved_wheel_event_info)
        super(WebView, self).wheelEvent(event)
        self.wheel_timer.stop()
        self.wheel_accumulator = 0


if __name__ == '__main__':
    from jigna.qt import QtGui
    app = QtGui.QApplication.instance() or QtGui.QApplication([])
    w = HTMLWidget()
    w.create()
    w.control.show()
    w.load_url('http://www.google.com/')
    app.exec_()
