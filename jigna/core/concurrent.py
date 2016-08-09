#
#
# (C) Copyright 2013-2016 Enthought, Inc., Austin, TX
# All right reserved.
#

"""Module to support asynchronous execution of code."""

# System library imports.
try:
    from __builtin__ import unicode as utext
except ImportError:
    from builtins import str as utext

import sys
from threading import Thread, RLock
from functools import wraps

# Enthought library imports.
from traits.api import (HasTraits, Any, Range, Undefined, Instance, Str,
    Property, Enum, ReadOnly, DelegatesTo, Event)


def set_trait_later(obj, trait, value):
    from ..utils import gui
    gui.set_trait_later(obj, trait, value)


################################################################################
# `Signal` class.
################################################################################

class Signal(HasTraits):
    """ A very simple object signal emitted with only one argument.

    Very similar (and inspired by) Qt's Signals, except that this is object
    based signal instead of class based descriptor signals, i.e., you don't
    need to define signals in the class body, you can directly use Signal
    by instantiating a Signal object.

    Usage:
    ------

        >>> s = Signal()
        >>> def func(arg):
        ...     print 'emitted:', arg
        >>> s.connect(func)
        >>> s.emit('value')
        emitted: value
        >>> s.disconnect(func)

    """
    _event = Event

    def connect(self, listener):
        self.on_trait_change(listener, '_event')

    def disconnect(self, listener):
        self.on_trait_change(listener, '_event', remove=True)

    def emit(self, value):
        self._event = value

def do_callback(dispatch, callback, *args):
    """Invoke the callback with a suitable dispatch.
    """
    if dispatch == 'ui':
        from ..utils.gui import invoke_later
        invoke_later(callback, *args)
    else:
        callback(*args)


################################################################################
# `Promise` class.
################################################################################

class Promise(HasTraits):
    """ The promise of a deferred operation, which can be used
    to add success, failure and progress callbacks for the operation.

    The Promise instance has a ``dispatch`` trait which can be set to "same" or
    "ui" and if it is set to "ui" all changes and callbacks are made in the GUI
    thread.

    """

    def __init__(self, **traits):
        HasTraits.__init__(self, **traits)
        # This should really be a reader-writer lock for performance, but this
        # will do for the time being.
        self._lock = RLock()


    # `Promise` Interface #####################################################
    def on_done(self, callback):
        """ Add callback for successful completion of the operation.
        """
        with self._lock:
            status = self._status
            if status == "pending":
                self.on_trait_change(lambda value: (self._status == 'done')
                                                    and callback(self._result),
                                    '_status', dispatch=self.dispatch)

        # Release the lock before calling the callback. Status is done so nothing
        # will mutate further - we are safe.
        if status == "done":
            do_callback(self.dispatch, callback, self._result)

    def on_error(self, callback):
        """ Add callback for failure of the operation.
        """
        with self._lock:
            status = self._status
            if status == "pending":
                self.on_trait_change(lambda value: (self._status == 'error')
                                                    and callback(self._error),
                                    '_status', dispatch=self.dispatch)

        # Release the lock before calling the callback. Status is done so nothing
        # will mutate further - we are safe.
        if status == "error":
            do_callback(self.dispatch, callback, self._error)

    def on_progress(self, callback):
        """ Add callback for progress of the operation.
        """
        with self._lock:
            status = self._status
            if status == "pending":
                self.on_trait_change(lambda value: callback(value),
                                     '_progress', dispatch=self.dispatch)

        # Release the lock before calling the callback. Status is done so nothing
        # will mutate further - we are safe.
        if self._status == 'done':
            # If operation is already completed, call with 1.0
            do_callback(self.dispatch, callback, self._progress)

    #################################
    # Traits.

    # Dispatch all callbacks either in the same thread or in the UI thread.
    dispatch = Enum('same', 'ui')

    # Status of the Promise.
    status = Property
    _status = Enum('pending', 'done', 'error')

    def _get_status(self):
        with self._lock:
            return self._status

    # The result, if any.
    result = Property
    _result = Any(Undefined)

    def _get_result(self):
        with self._lock:
            if self._status == 'pending':
                raise ValueError('Promise not completed yet')
            else:
                return self._result

    # The error, if any.
    error = Property
    _error = Any(Undefined)

    def _get_error(self):
        with self._lock:
            if self._status == 'pending':
                raise ValueError('Promise not completed yet')
            else:
                return self._error

    # The progress.
    progress = Property
    _progress = Range(0.0, 1.0, 0.0)

    def _get_progress(self):
        with self._lock:
            return self._progress



################################################################################
# `Deferred` class.
################################################################################
class Deferred(HasTraits):
    """ A Deferred operations which will complete in the future.

    Usage:
    ------
    In an asynchronous method which would normally require you to accept a
    callback method, you can use the Deferred object to let callers add
    callbacks even after making the call, in fact even after the operation
    has finished.

    The following example illustrates the simplest use of a Future::

        def background_job():
            deferred = Deferred()
            # Some async job which takes a callback
            async_background_job(callback=lambda result: deferred.done(result))
            return deferred.promise()

        def on_job_finished(self, result):
            print result

        bg_job = background_job()
        # bg_job promise can be used add callbacks
        bg_job.on_done(on_job_finished)

    The advantages of this approach to passing callbacks are:
        - ability to add callbacks after the call has been made
        - ability to add callbacks even after the function has returned
        - pass around promise objects to let others add callacks for the job
          This can be useful for example to add a progress feature to
          an existing function which would have otherwise needed to add
          an extra progress_callback argument.

    The Deferred supports two dispatch mechanisms, "same" and "ui" if the
    ``dispatch`` trait is set to "ui" all attributes are set on the GUI thread
    and all callbacks are also called from the UI thread.

    Notes:
    ------
    Always return the promise() object for an operation to callers when using
    Deferred so that so that they can only add callbacks and not set result.

    """
    # `Deferred` Interface ####################################################
    def done(self, value):
        """ Complete the deferred with success and specified result.
            and set the progress to 1.0
        """
        if self.dispatch == 'ui':
            promise = self.promise
            set_trait_later(promise, '_result', value)
            set_trait_later(promise, '_progress', 1.0)
            set_trait_later(promise, '_status', 'done')
        else:
            with self.promise._lock:
                self.promise._result = value
                self.promise._progress = 1.0
                self.promise._status = 'done'

    def error(self, value):
        """ Complete the deferred with failure and specified result. """
        if self.dispatch == 'ui':
            promise = self.promise
            set_trait_later(promise, '_error', value)
            set_trait_later(promise, '_status', 'error')
        else:
            with self.promise._lock:
                self.promise._error = value
                self.promise._status = 'error'

    def progress(self, value):
        """ Set the progress of the operation (0 <= value <= 1). """
        if self.dispatch == 'ui':
            set_trait_later(self.promise, '_progress', value)
        else:
            with self.promise._lock:
                self.promise._progress = value

    # Traits ##################################################################

    # Dispatch all callbacks either in the same thread or in the UI thread.
    dispatch = Enum('same', 'ui')

    promise = ReadOnly(Instance(Promise))

    def _promise_default(self):
        return Promise(dispatch=self.dispatch)


################################################################################
# `Future` class.
################################################################################
class Future(Promise):

    """
    This could be used for any long-running call that needs to run on
    another thread.  The result of the call is stored in the `result` trait.
    Accessing the `result` trait will block till the thread completes its task.
    The `done` method can be used to check if the thread has completed.
    Optional progress information is available in a `progress` trait.
    Additional optional information is also available in the `info` trait.

    One can also set the ``dispatch`` mode to "ui" in which case all
    changes to attributes and callbacks are made on the GUI thread.

    The following example illustrates the simplest use of a Future::

        >>> import time
        >>> x = Future(lambda : time.sleep(1) or 'done')
        >>> assert x.done() is False
        >>> assert x.result == 'done' # This will block.

    Here is a slightly more complex example illustrating the use of the
    ``f_on_progress`` and ``f_on_status`` callbacks::

        >>> def on_progress(future):
        ...    print future.progress
        ...
        >>> def on_status(future):
        ...    if future.status == 'done':
        ...        print future.result
        ...    elif future.status == 'error':
        ...        print future.error
        ...
        >>> def compute(future=None):
        ...     for i in range(5):
        ...         if future is not None:
        ...             future.info = str(i)
        ...             future.progress = (i+1)*0.2
        ...         time.sleep(0.1)
        ...     return 'done'
        ...
        >>> x = Future(compute, f_on_status=on_status,
        ...            f_on_progress=on_progress, future_kw='future')
        >>> for i in range(5):
        ...     print x.progress, x.info
        ...     time.sleep(0.1)
        ...
        >>> print x.result

    """

    # Status of the Future.
    status = DelegatesTo('promise', 'status')

    # The result of the call. When accessed this will block unless the
    # thread has finished execution.
    result = Property(Any, depends_on='status')

    # The exception if any.  ``sys.exc_info`` is stored here.
    error = DelegatesTo('promise', 'error')

    # Progress information.
    progress = Property(depends_on='promise._progress')

    # Optional information.
    info = Str('')

    #################################
    # Private Traits.

    # The thread in which the function is running.
    _thread = Instance(Thread)

    # The Deferred object for the operation and its promise.
    _deferred = Instance(Deferred)
    promise = DelegatesTo('_deferred', 'promise')

    ############################################################################
    # `object` interface.
    ############################################################################
    def __init__(self, func, f_on_status=None, f_on_progress=None,
                 future_kw=None, dispatch='same', args=None, kw=None):
        """Constructor for a Future.

        If an exception is raised when the future runs, ``sys.exc_info()``
        is stored in the error trait and the ``status`` is set to "error"

        Parameters
        ----------

        func : callable
            The callable to execute in another thread.

        f_on_status : callable
            The callable to callback when the status is changed.  This function
            will be passed the `Future` instance as a single argument.

        f_on_progress : callable
            The callable to callback when the progress is changed. This function
            will be passed the `Future` instance as a single argument.

        future_kw : str
            The keyword argument of the callable that accepts a `Future`
            instance, typically used for progress info.

        args : additional args
            These are passed on to the callable.

        kw : additional keyword args
            Passed to the callable, ``func``.

        """
        # Set this first.
        self.dispatch = dispatch
        super(Future, self).__init__()

        if f_on_progress is not None:
            self.on_progress(lambda value:f_on_progress(self))

        if f_on_status:
            self.on_done(lambda value:f_on_status(self))
            self.on_error(lambda value:f_on_status(self))

        # The wrapper function to call in a thread.
        def _f(self, *args, **kw):
            """This function is called by the `Thread` instance."""
            try:
                self._deferred.done(func(*args, **kw))
            except:
                self._deferred.error(sys.exc_info())

        # Pass self to the function if it needs it.
        if future_kw is not None and type(future_kw) in (str, utext):
            kw[future_kw] = self
        args = args or ()
        kw = kw or {}
        t = Thread(target=_f, args=(self,) + args, kwargs=kw)
        self._thread = t
        t.daemon = True
        t.start()

    ############################################################################
    # `Future` interface.
    ############################################################################
    def done(self):
        """Return True if the future has completed execution."""
        return self.promise.status != 'pending'

    ############################################################################
    # `Promise` interface.
    ############################################################################
    def on_done(self, callback):
        self.promise.on_done(callback)

    def on_error(self, callback):
        self.promise.on_error(callback)

    def on_progress(self, callback):
        self.promise.on_progress(callback)

    ############################################################################
    # Trait handlers.
    ############################################################################
    def _get_result(self):
        # _status is synchronized, so copy local to avoid constant lock acquisitions
        status = self.promise._status
        if status == 'pending':
            self._thread.join()
            # Status will have switched to "done" or "error"
            status = self.promise._status

        if status == 'done':
            return self.promise.result
        else:
            return Undefined

    def _get_progress(self):
        return self.promise.progress

    def _set_progress(self, val):
        self._deferred.progress(val)

    def __deferred_default(self):
        return Deferred(dispatch=self.dispatch)

################################################################################
# `threaded` decorator.
################################################################################
def threaded(func=None, f_on_status=None, f_on_progress=None, future_kw=None,
             dispatch='same'):
    """ A decorator to run a function in a separate thread and return a
    `Future` object which will store the results when the function completes.

    Parameters
    ----------

    future_kw : str
        The keyword argument of the decorated function that accepts a `Future`
        instance.

    f_on_status : callable
        The callable to callback when the status is changed.  This function
        will be passed the `Future` instance as a single argument.

    f_on_progress : callable
        The traits handler to callback when the progress is changed. Note
        that this is a traits handler.

    dispatch : str
        The dispatch mechanism to use.  One of either 'same' or 'ui'.

    Examples
    ---------

    The following examples illustrates its usage::

        >>> import time
        >>> @threaded
        ... def compute(x):
        ...     # long running computation
        ...     time.sleep(x)
        ...     return x
        >>> a = f(0.5)
        >>> b = f(1.0)
        >>> print a.result, b.result

        >>> @threaded(future_kw='future')
        ... def compute_with_progress(dt, future):
        ...     for i in range(10):
        ...         time.sleep(dt)
        ...         future.progress = (i+1)*0.1
        ...     return time.time()
        ...
        >>> a = compute_with_progress(0.1)
        >>> # Future is automatically passed.
    """

    def future_decorator(func, f_on_status=f_on_status,
                         f_on_progress=f_on_progress,
                         future_kw=future_kw, dispatch=dispatch):
        def _wrapper(*args, **kw):
            """The wrapper function."""
            return Future(func, f_on_status, f_on_progress, future_kw,
                          dispatch, *args, **kw)
        return wraps(func)(_wrapper)

    if func is None:
        return future_decorator
    else:
        return future_decorator(func, f_on_status, f_on_progress,
                                future_kw=future_kw, dispatch=dispatch)
