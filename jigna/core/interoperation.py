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
from pyface.qt import QtCore

# Logger.
logger = logging.getLogger(__name__)

###############################################################################
# Functions.
###############################################################################

class PythonContainer(QtCore.QObject):
    """ Container class for python object to be exposed to js. """
    def __init__(self, parent=None, slot_map=None, wrapped_obj=None):
        super(PythonContainer, self).__init__(parent)

        # slot_name: callable
        self._slot_map = slot_map

        # the object being wrapped for property access
        self._wrapped_obj = wrapped_obj


def create_js_object_wrapper(obj, callbacks=[], properties=[], parent=None):
    """ Create an object wrapper for python objects.

    Usage:
    ------
    1. Auto wrap python objects:

       Call with a python object as `obj` and both `callbacks` and `properties`
       unspecified. Any attributes of `obj` wrappable in JS will be wrapped.

    2. Wrap specified attributes of object:

       Call with `callbacks` and `properties` as a list of attributes to be
       exposed to JS.

       Each element of the list must be either:
        - str, which is taken as the attribute name of `obj` to be
          exposed to JS with same name and whose value is the value of
          the attribute of `obj`
        - 2-tuple (str,obj/callable), where the second element object
          exposed to JS with first element str as the property name.
          In this case the argument `obj` is unused.

    Note: Arbitrary object cannot be wrapped and callables in the form of
    function objects cannot be exposed as functions in JS. If `obj` is a dict,
    the items of the dict are exposed instead of the attributes.

    Note: Set the parent (setParent()) of the returned QObject to make sure
    it is destroyed when the parent is destroyed, or manually destroy the
    object when it is no longer needed (such as when the `window` js object
    is cleared or the webview/webpage/webframe object is destroyed);
    else stray references to the object may cause memory leaks.

    """
    if isinstance(obj, dict):
        obj = type('CustomObject', (object,), obj)

    # Create the container class dict.
    class_dict = {}
    auto = not callbacks and not properties
    if auto:
        names = filter(lambda name: not name.startswith('_'), dir(obj))
        is_callable = lambda name: callable(getattr(obj, name))
        callbacks, properties = split_on_condition(names, is_callable)

    # Create the container callback slots, these need to be defined on the
    # class (associated with the QMetaObject).
    slot_map = {}
    for name_or_pair in callbacks:
        if isinstance(name_or_pair, basestring):
            name = name_or_pair
            callback = getattr(obj, name)
        else:
            name, callback = name_or_pair

        wrapped = wrap_func(callback, name)
        if wrapped:
            class_dict[name] = wrapped
            slot_map[wrapped.name] = callback
        elif not auto:
            logger.error('Callback %r is not translatable to JavaScript', name)

    # Create the container properties.
    for name_or_pair in properties:
        if isinstance(name_or_pair, basestring):
            jname, pname = name_or_pair, name_or_pair
        else:
            jname, pname = name_or_pair

        qproperty = wrap_property(obj, pname)
        if qproperty:
            class_dict[jname] = qproperty
        elif not auto:
            logger.error('Attribute %r is not translatable to JavaScript',
                         pname)

    # Create the container class.
    container_class = type('CustomPythonContainer', (PythonContainer, QtCore.QObject,), class_dict)
    qobj = container_class(parent=parent, slot_map=slot_map, wrapped_obj=obj)

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

def wrap_property(obj, name, setter=True):
    """ Wraps a Python attribute as a Qt Property.
    """
    getter = lambda self: getattr(self._wrapped_obj, name)
    if setter:
        setter = lambda self, value: setattr(self._wrapped_obj, name, value)
    value = getattr(obj, name)
    signature = None
    if isinstance(value, dict):
        signature = 'QVariantMap'
    elif isinstance(value, list):
        signature = 'QVariantList'
    elif isinstance(value, (bool, int, long, float, basestring)):
        signature = 'QVariant'
    if signature:
        if setter:
            return QtCore.Property(signature, getter, setter)
        else:
            return QtCore.Property(signature, getter)
    return None

def split_on_condition(seq, condition):
    """ Split a list on a condition.
    """
    a, b = [], []
    for item in seq:
        (a if condition(item) else b).append(item)
    return a, b
