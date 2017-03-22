""" Simple minimal compatibility code for using PyQt4 and PySide
interchangeably only to the extent needed by jigna.

"""


def load_pyside():
    global QtCore, QtGui, QtNetwork, QtWebKit
    from PySide import QtCore, QtGui, QtNetwork, QtWebKit


def load_pyqt():
    global QtCore, QtGui, QtNetwork, QtWebKit

    import sip
    sip.setapi('QDate', 2)
    sip.setapi('QDateTime', 2)
    sip.setapi('QString', 2)
    sip.setapi('QTextStream', 2)
    sip.setapi('QTime', 2)
    sip.setapi('QUrl', 2)
    sip.setapi('QVariant', 2)

    from PyQt4 import QtCore, QtGui, QtNetwork, QtWebKit, Qt

    QtCore.Property = QtCore.pyqtProperty
    QtCore.Signal = QtCore.pyqtSignal
    QtCore.Slot = QtCore.pyqtSlot


def main():

    import os
    import sys

    if os.environ.get('QT_API') == 'pyside' or 'PySide' in sys.modules:
        load_pyside()
    elif os.environ.get('QT_API') == 'pyqt' or 'PyQt4' in sys.modules:
        load_pyqt()
    else:
        try:
            load_pyqt()
        except ImportError:
            load_pyside()

main()

