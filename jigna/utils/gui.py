# Local imports
from ..qt import QtGui, QtCore

def ui_handler(handler, *args, **kw):
    """ Handles UI notification handler requests that occur on a thread other
    than the UI thread.
    """
    _CallAfter(handler, *args, **kw)

def set_trait_later(obj, trait_name, value):
    invoke_later(setattr, obj, trait_name, value)

def invoke_later(callable, *args, **kw):
    """ Invoke the callable in the GUI thread.
    """
    do_after(0, callable, *args, **kw)

def do_after(ms, callable, *args, **kw):
    _FutureCall(ms, callable, *args, **kw)

#### Private protocol #########################################################

class _CallAfter(QtCore.QObject):
    """ This class dispatches a handler so that it executes in the main GUI
    thread (similar to the wx function).
    """

    # The list of pending calls.
    _calls = []

    # The mutex around the list of pending calls.
    _calls_mutex = QtCore.QMutex()

    # A new Qt event type for _CallAfters
    _QT_TRAITS_EVENT = QtCore.QEvent.Type(QtCore.QEvent.registerEventType())

    def __init__(self, handler, *args, **kwds):
        """ Initialise the call.
        """
        QtCore.QObject.__init__(self)

        # Save the details of the call.
        self._handler = handler
        self._args = args
        self._kwds = kwds

        # Add this to the list.
        self._calls_mutex.lock()
        self._calls.append(self)
        self._calls_mutex.unlock()

        # Move to the main GUI thread.
        self.moveToThread(QtGui.QApplication.instance().thread())

        # Post an event to be dispatched on the main GUI thread. Note that
        # we do not call QTimer.singleShot, which would be simpler, because
        # that only works on QThreads. We want regular Python threads to work.
        event = QtCore.QEvent(self._QT_TRAITS_EVENT)
        QtGui.QApplication.instance().postEvent(self, event)

    def event(self, event):
        """ QObject event handler.
        """
        if event.type() == self._QT_TRAITS_EVENT:
            # Invoke the handler
            self._handler(*self._args, **self._kwds)

            # We cannot remove from self._calls here. QObjects don't like being
            # garbage collected during event handlers (there are tracebacks,
            # plus maybe a memory leak, I think).
            QtCore.QTimer.singleShot(0, self._finished)

            return True
        else:
            return QtCore.QObject.event(self, event)

    def _finished(self):
        """ Remove the call from the list, so it can be garbage collected.
        """
        self._calls_mutex.lock()
        del self._calls[self._calls.index(self)]
        self._calls_mutex.unlock()


class _FutureCall(QtCore.QObject):
    """ This is a helper class that is similar to the wx FutureCall class. """

    # Keep a list of references so that they don't get garbage collected.
    _calls = []

    # Manage access to the list of instances.
    _calls_mutex = QtCore.QMutex()

    # A new Qt event type for _FutureCalls
    _pyface_event = QtCore.QEvent.Type(QtCore.QEvent.registerEventType())

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
        event = QtCore.QEvent(self._pyface_event)
        QtGui.QApplication.postEvent(self, event)
        QtGui.QApplication.sendPostedEvents()

    def event(self, event):
        """ QObject event handler.
        """
        if event.type() == self._pyface_event:
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