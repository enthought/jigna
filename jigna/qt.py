""" Simple minimal compatibility code for using PyQt4 and PySide
interchangeably only to the extent needed by jigna.

"""

QT_API_PYSIDE = 'pyside'
QT_API_PYQT4 = 'pyqt'
QT_API_PYQT5 = 'pyqt5'


def load_pyside():
    global qt_api
    global QtCore, QtGui, QtWidgets, QtNetwork, QtWebKit, QtWebKitWidgets
    qt_api = QT_API_PYSIDE
    from PySide import (
        QtCore, QtGui, QtNetwork, QtWebKit,
        QtWebKit as QtWebKitWidgets, QtGui as QtWidgets)


def load_pyqt5():
    global qt_api
    global QtCore, QtGui, QtWidgets, QtNetwork, QtWebKit, QtWebKitWidgets
    qt_api = QT_API_PYQT5
    from PyQt5 import (
        QtCore, QtGui, QtNetwork, QtWebKit, QtWebKitWidgets, QtWidgets)


def load_pyqt4():
    global qt_api
    global QtCore, QtGui, QtWidgets, QtNetwork, QtWebKit, QtWebKitWidgets

    qt_api = QT_API_PYQT4

    import sip
    sip.setapi('QDate', 2)
    sip.setapi('QDateTime', 2)
    sip.setapi('QString', 2)
    sip.setapi('QTextStream', 2)
    sip.setapi('QTime', 2)
    sip.setapi('QUrl', 2)
    sip.setapi('QVariant', 2)

    from PyQt4 import (
        QtCore, QtGui, QtNetwork, QtWebKit,
        QtWebKit as QtWebKitWidgets, QtGui as QtWidgets)

    QtCore.Property = QtCore.pyqtProperty
    QtCore.Signal = QtCore.pyqtSignal
    QtCore.Slot = QtCore.pyqtSlot


def main():
    import os
    import sys

    if os.environ.get('QT_API') == QT_API_PYQT5 or 'PyQt5' in sys.modules:
        load_pyqt5()
    elif os.environ.get('QT_API') == QT_API_PYQT4 or 'PyQt4' in sys.modules:
        load_pyqt4()
    elif os.environ.get('QT_API') == QT_API_PYSIDE or 'PySide' in sys.modules:
        load_pyside()
    else:
        try:
            load_pyqt5()
        except ImportError:
            try:
                load_pyqt4()
            except ImportError:
                load_pyside()

main()
