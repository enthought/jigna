#
# Jigna product code
#
# (C) Copyright 2013 Enthought, Inc., Austin, TX
# All right reserved.
#

# Standard library imports.
try:
    from __builtin__ import unicode
except ImportError:
    from builtins import str as unicode

import logging
import sys
import threading
from io import StringIO

# System library imports.
from jigna.qt import QtCore, QtNetwork

# Logger.
logger = logging.getLogger(__name__)


class ProxyAccessManager(QtNetwork.QNetworkAccessManager):
    """ A QNetworkAccessManager subclass which proxies requests for a set of
    hosts and schemes.
    """
    def __init__(self, root_paths={}, hosts={}):
        """ root_paths: Mapping of root paths to WSGI callables.
            hosts: Mapping of hosts to WSGI callables.
        """
        super(ProxyAccessManager, self).__init__()
        self.root_paths = root_paths
        self.hosts = hosts

    def get_url_handler(self, url):
        """ Returns the WSGI callable to be used for specified url.
        """
        handler = self.hosts.get(url.host())

        if handler is None:
            for root, _handler in self.root_paths.items():
                if url.path().split('/')[1] == root:
                    handler = _handler

        return handler

    def inject(self, webview):
        """ Replace the old QNetworkAccessManager instance with this instance.
        """
        old_manager = webview.page().networkAccessManager()

        self.setCache(old_manager.cache())
        self.setCookieJar(old_manager.cookieJar())
        self.setProxy(old_manager.proxy())
        self.setProxyFactory(old_manager.proxyFactory())
        webview.page().setNetworkAccessManager(self)

    ###########################################################################
    # QNetworkAccessManager interface
    ###########################################################################

    def createRequest(self, operation, request, data):
        """ Create a ProxyReply request if url handler is provided by
        `hosts`, else defer to the original QNetworkAccessManager
        `createRequest` method.
        """
        url = request.url()
        handler = self.get_url_handler(url)
        if handler is not None:
            data_str = data and data.readAll() or ''
            return ProxyReply(self, url, operation, request, data_str, handler)

        # Default case, let superclass handle normal web access
        return super(ProxyAccessManager, self).createRequest(
            operation, request, data
        )


class ProxyReply(QtNetwork.QNetworkReply):
    """ QNetworkReply subclass to send a specific request to local wsgi app.
    """
    def __init__(self, parent, url, operation, req, data, handler):
        """ handler is the wsgi app """

        super(ProxyReply, self).__init__(parent)

        self.setRequest(req)
        self.setOperation(operation)
        self.setUrl(url)

        self.req_data = data
        self.handler = handler

        self.buffer = b''
        self._buflock = threading.Lock()
        self.aborted = False

        self.open(self.ReadOnly)

        self._worker = ProxyReplyWorker(self)
        self._worker.start()

        # Handle synchronous requests (webkit sync ajax requests)
        # req.Attribute.QSynchronousHttpNetworkReply may not be defined for
        # pyside compiled with qt 4.7 but still works with qt 4.8
        # QSynchronousHttpNetworkReply = DownloadBufferAttribute + 1 = 16
        if req.attribute(req.Attribute(16)):
            self._worker.wait()

    ###########################################################################
    # QNetworkReply interface
    ###########################################################################

    def abort(self):
        if not self.aborted:
            self.aborted = True
            self.setError(self.OperationCanceledError,
                          'Request Aborted')

    def bytesAvailable(self):
        return super(ProxyReply, self).bytesAvailable() + len(self.buffer)

    def isSequential(self):
        return True

    def readData(self, maxSize):
        with self._buflock:
            data, self.buffer = self.buffer[:maxSize], self.buffer[maxSize:]
        return data


class ProxyReplyWorker(QtCore.QThread):
    """ Worker thread to fetch urls for QNetworkProxy. """

    # Signals to forward to ProxyReply
    metaDataChanged = QtCore.Signal()
    readyRead = QtCore.Signal()
    finished = QtCore.Signal()

    OPERATIONS = {QtNetwork.QNetworkAccessManager.GetOperation: 'GET',
                  QtNetwork.QNetworkAccessManager.PostOperation: 'POST',}

    def __init__(self, reply, parent=None):
        super(ProxyReplyWorker, self).__init__(parent)
        self.reply = reply
        self.metaDataChanged.connect(self.reply.metaDataChanged)
        self.readyRead.connect(self.reply.readyRead)
        self.finished.connect(self.reply.finished)

    ###########################################################################
    # QThread interface.
    ###########################################################################

    def run(self):
        """ handles the request by acting as a WSGI forwarding server. """
        reply = self.reply
        url = reply.url()
        req = reply.request()

        # WSGI environ variables
        env = {
            'REQUEST_METHOD': self.OPERATIONS[reply.operation()],
            'SCRIPT_NAME': '',
            'PATH_INFO': url.path(),
            'SERVER_NAME': url.host(),
            'SERVER_PORT': '80',
            'SERVER_PROTOCOL': 'HTTP/1.1',
            'QUERY_STRING': str(url.encodedQuery()),
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': url.scheme(),
            'wsgi.input': StringIO(unicode(reply.req_data)),
            'wsgi.errors': sys.stderr,
            'wsgi.multithread': False,
            'wsgi.multiprocess': True,
            'wsgi.run_once': False,
        }

        # Set WSGI HTTP request headers
        for head_name in req.rawHeaderList():
            env_name = 'HTTP_' + head_name.data().decode().replace('-','_').upper()
            head_val = req.rawHeader(head_name)
            env[env_name] = head_val.data()

        try:
            local_buf = []
            local_buf_len = 0
            for read in reply.handler(env, self._start_response):
                if reply.aborted:
                    return
                if not isinstance(read, bytes):
                    read = str(read).encode('utf8')
                local_buf.append(read)
                local_buf_len += len(read)
                if local_buf_len >= 8192:
                    # Do not write to buffer on every read, app is slowed down
                    # due to lock contention
                    with reply._buflock:
                        reply.buffer += b''.join(local_buf)
                    local_buf = []
                    local_buf_len = 0
                    self.readyRead.emit()
            with reply._buflock:
                reply.buffer += b''.join(local_buf)

        except Exception as e:
            if reply.aborted:
                return
            reply.setAttribute(
                QtNetwork.QNetworkRequest.HttpStatusCodeAttribute, 500
            )
            reply.setAttribute(
                QtNetwork.QNetworkRequest.HttpReasonPhraseAttribute,
                'Internal Error'
            )
            with reply._buflock:
                reply.buffer += b'WSGI Proxy "Server" Error.\n' + str(e)
        finally:
            self.readyRead.emit()
            self.finished.emit()

    ###########################################################################
    # Private interface.
    ###########################################################################

    def _start_response(self, status, response_headers):
        """ WSGI start_response callable. """
        code, reason = status.split(' ', 1)
        self.reply.setAttribute(
            QtNetwork.QNetworkRequest.HttpStatusCodeAttribute, int(code)
        )
        self.reply.setAttribute(
            QtNetwork.QNetworkRequest.HttpReasonPhraseAttribute, reason
        )
        for name, value in response_headers:
            self.reply.setRawHeader(name, str(value))

        self.metaDataChanged.emit()
