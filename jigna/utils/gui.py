# Standard library imports
import sys

# Local imports
from ..qt import QtGui, QtCore

def ui_handler(handler, *args, **kw):
    """ Handles UI notification handler requests that occur on a thread other
    than the UI thread.
    """
    invoke_later(handler, *args, **kw)

def set_trait_later(obj, trait_name, value):
    """ Set the given trait name on the given object in the GUI thread.
    """
    invoke_later(setattr, obj, trait_name, value)

def invoke_later(callable, *args, **kw):
    """ Invoke the callable in the GUI thread.
    """
    _FutureCall(0, callable, *args, **kw)

def do_after(ms, callable, *args, **kw):
    """ Invoke the callable after the given number of milliseconds.
    """
    app = QtGui.QApplication.instance() or QtGui.QApplication(sys.argv)
    QtCore.QTimer.singleShot(ms, lambda : callable(*args, **kw))

def process_events():
    """ Process all events.
    """
    QtCore.QCoreApplication.processEvents(QtCore.QEventLoop.AllEvents)

#### Private protocol #########################################################

class _FutureCall(QtCore.QObject):
    """ This is a helper class to facilitate execution of a function in the
    future (after all events are finished processing) in the GUI thread.
    """

    # Keep a list of references so that they don't get garbage collected.
    _calls = []

    # Manage access to the list of instances.
    _calls_mutex = QtCore.QMutex()

    # A new Qt event type for _FutureCalls
    _gui_event = QtCore.QEvent.Type(QtCore.QEvent.registerEventType())

    def __init__(self, ms, callable, *args, **kw):
        super(_FutureCall, self).__init__()

        # Save the arguments.
        self._ms = ms
        self._callable = callable
        self._args = args
        self._kw = kw

        # Save the instance.
        self._calls_mutex.lock()
        self._calls.append(self)
        self._calls_mutex.unlock()

        # Move to the main GUI thread.
        self.moveToThread(QtGui.QApplication.instance().thread())

        # Post an event to be dispatched on the main GUI thread. Note that
        # we do not call QTimer.singleShot here, which would be simpler, because
        # that only works on QThreads. We want regular Python threads to work.
        event = QtCore.QEvent(self._gui_event)
        QtGui.QApplication.postEvent(self, event)
        QtGui.QApplication.sendPostedEvents()

    def event(self, event):
        """ QObject event handler.
        """
        if event.type() == self._gui_event:
            # Invoke the callable (puts it at the end of the event queue)
            QtCore.QTimer.singleShot(self._ms, self._dispatch)
            return True

        return super(_FutureCall, self).event(event)

    def _dispatch(self):
        """ Invoke the callable.
        """
        try:
            self._callable(*self._args, **self._kw)
        finally:
            self._finished()

    def _finished(self):
        """ Remove the call from the list, so it can be garbage collected.
        """
        self._calls_mutex.lock()
        try:
            self._calls.remove(self)
        finally:
            self._calls_mutex.unlock()