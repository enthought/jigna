# Standard library imports
import json

# Local imports
from ..qt import QtGui, QtCore

def serialize(obj):
    """ Convert a python object to JS by serialization/deserialization. If one
    of the traits could not be converted, it's possibly a HasTraits object,
    in which case, it is serialized by repeating the process for that trait.
    """
    try:
        serialized = json.dumps(obj)
    except TypeError:
        serialized = json.dumps(None)
    return serialized

def get_value(obj, extended_trait_name):
    """ Obtain the value of given extended_trait_name of obj. An `extended_trait_name`
    should be same as the python syntax that is used to refer to the concerned
    variable.
    """
    return eval('obj.'+extended_trait_name, {'obj': obj})

def ui_handler(handler, *args, **kwds):
    """ Handles UI notification handler requests that occur on a thread other
    than the UI thread.
    """
    _CallAfter(handler, *args, **kwds)

#### Private protocol #########################################################

class _CallAfter(QtCore.QObject):
    """ This class dispatches a handler so that it executes in the main GUI
        thread (similar to the wx function).
    """

    _QT_TRAITS_EVENT = QtCore.QEvent.Type(QtCore.QEvent.registerEventType())

    # The list of pending calls.
    _calls = []

    # The mutex around the list of pending calls.
    _calls_mutex = QtCore.QMutex()

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
