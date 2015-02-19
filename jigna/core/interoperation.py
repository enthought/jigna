#
# Jigna product code
#
# (C) Copyright 2013 Enthought, Inc., Austin, TX
# All right reserved.
#

# Standard library imports.
import inspect
import logging

# System library imports.
from jigna.qt import QtCore

# Logger.
logger = logging.getLogger(__name__)

def create_js_object_wrapper(callbacks=[], parent=None):
    """ Create a JS object wrapper containing the given callbacks as its
    methods.

    Note: Set the parent (setParent()) of the returned QObject to make sure
    it is destroyed when the parent is destroyed, or manually destroy the
    object when it is no longer needed (such as when the `window` js object
    is cleared or the webview/webpage/webframe object is destroyed);
    else stray references to the object may cause memory leaks.

    """
    # Create the container class dict.
    class_dict = {}

    # Create the container callback slots, these need to be defined on the
    # class (associated with the QMetaObject).
    slot_map = {}
    for _callback in callbacks:
        name, callback = _callback

        wrapped = wrap_func(callback, name)
        if wrapped:
            class_dict[name] = wrapped
            slot_map[wrapped.name] = callback
        else:
            logger.error('Callback %r is not translatable to JavaScript', name)

    # Create the container class.
    container_class = type(
        'CustomPythonContainer', (_PythonContainer, QtCore.QObject,), class_dict
    )
    qobj = container_class(parent=parent, slot_map=slot_map)

    return qobj

def wrap_func(func, name=None):
    """ Wraps a Python callable as a Qt Slot.
    """
    try:
        args = inspect.getargspec(func).args
    except TypeError:
        return None

    if args and args[0] in ('self', 'cls'):
        args.pop(0)
    types = ['QVariant'] * len(args)

    slot_key = name if name is not None else 'func_' + hex(id(func))

    @QtCore.Slot(*types, name=name, result='QVariant')
    def wrapped(self, *args):
        return self._slot_map[slot_key](*args)
    wrapped.name = slot_key
    return wrapped

#### Private protocol #########################################################

class _PythonContainer(QtCore.QObject):
    """ Container class for python object to be exposed to js. """
    def __init__(self, parent=None, slot_map=None):
        super(_PythonContainer, self).__init__(parent)

        # slot_name: callable
        self._slot_map = slot_map