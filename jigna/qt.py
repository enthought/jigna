""" Simple minimal compatibility code for using PyQt4 and PySide
interchangeably only to the extent needed by jigna.

"""

qt_api = None


def load_pyside():
    global QtCore, QtGui, QtNetwork, QtWebKit, QtWebEngine, qt_api
    from PySide import QtCore, QtGui, QtNetwork, QtWebKit
    QtWebEngine = None
    qt_api = 'pyside'


def load_pyqt():
    global QtCore, QtGui, QtNetwork, QtWebKit, QtWebEngine, qt_api

    import sip
    sip.setapi('QDate', 2)
    sip.setapi('QDateTime', 2)
    sip.setapi('QString', 2)
    sip.setapi('QTextStream', 2)
    sip.setapi('QTime', 2)
    sip.setapi('QUrl', 2)
    sip.setapi('QVariant', 2)

    from PyQt4 import QtCore, QtGui, QtNetwork, QtWebKit, Qt
    QtWebEngine = None
    QtCore.Property = QtCore.pyqtProperty
    QtCore.Signal = QtCore.pyqtSignal
    QtCore.Slot = QtCore.pyqtSlot

    qt_api = 'pyqt'


def load_pyqt5():
    global QtCore, QtGui, QtNetwork, QtWebKit, QtWebEngine, qt_api

    import types
    from PyQt5 import QtCore, QtGui, QtWidgets, QtNetwork, Qt

    def _union_mod(*mods):
        mod = types.ModuleType(mods[0].__name__)
        for _mod in mods:
            mod.__dict__.update(_mod.__dict__)
        return mod

    QtCore = _union_mod(QtCore)
    QtGui = _union_mod(QtGui, QtWidgets)

    QtCore.Property = QtCore.pyqtProperty
    QtCore.Signal = QtCore.pyqtSignal
    QtCore.Slot = QtCore.pyqtSlot

    QtWebEngine = QtWebKit = None

    try:
        from PyQt5 import QtWebKit, QtWebKitWidgets
        QtWebKit = _union_mod(QtWebKit, QtWebKitWidgets)
    except ImportError:
        pass
    try:
        from PyQt5 import QtWebEngine, QtWebEngineWidgets
        QtWebEngine = _union_mod(QtWebEngine, QtWebEngineWidgets)
    except ImportError:
        pass

    qt_api = 'pyqt5'


def main():

    import os
    import sys

    if os.environ.get('QT_API') == 'pyside' or 'PySide' in sys.modules:
        load_pyside()
    elif os.environ.get('QT_API') == 'pyqt' or 'PyQt4' in sys.modules:
        load_pyqt()
    elif os.environ.get('QT_API') == 'pyqt5' or 'PyQt5' in sys.modules:
        load_pyqt5()
    else:
        try:
            load_pyqt()
        except ImportError:
            try:
                load_pyside()
            except ImportError:
                load_pyqt5()

main()

if qt_api == 'pyqt5':
    def query_from_url(qurl):
        return qurl.query()

else:
    def query_from_url(qurl):
        return str(qurl.encodedQuery())
