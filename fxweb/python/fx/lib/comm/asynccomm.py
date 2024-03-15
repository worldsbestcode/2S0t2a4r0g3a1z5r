"""
asynccomm.py

Asynchronous tools for the MultiConnectionLibrary
"""

from threading import Thread
from functools import wraps, partial
import traceback
import types
import time

class ExcThread(Thread):
    """
    Class that runs in a thread and catches exceptions
    """

    def run(self):
        """ Overwrites run to throw any exceptions in the thread """
        self.exc = None
        try:
            Thread.run(self)
        except:
            self.exc = traceback.format_exc()

    def join(self):
        """ Overwrites join to catch any exceptions """
        Thread.join(self)
        if self.exc:
            raise AssertionError(self.exc)


def run_async(func):
    """
    Function decorator, intended to make "func" run in a separate
    thread (asynchronously).
    Returns the created Thread object

    Eg:
    @run_async
    def task1():
        do_something

    @run_async
    def task2():
        do_something_too

    t1 = task1()
    t2 = task2()
    ...
    t1.join()
    t2.join()
    """

    @wraps(func)
    def async_func(*args, **kwargs):
        func_hl = ExcThread(target = func, args = args, kwargs = kwargs)
        func_hl.start()
        return func_hl

    return async_func

def run_async_interval(delay_secs, daemon_mode):
    """
    Function decorator, intended to make "func" run in a separate
    thread (asynchronously) every few seconds.
    Returns the created Thread object

    Eg:
    delay_secs = 5

    @run_async_interval(delay_secs, False)
    def task1():
        do_something

    @run_async_interval(delay_secs, True)
    def task2():
        do_something_too

    t1 = task1()
    t2 = task2()
    ...
    t1.join()    # Join must be explicitly called on t1 to prevent blocking the
                 # main thread from exiting

    t2.join()    # You can optionally call join on t2 if you want to give the 
                 # thread time to exit, otherwise it will be killed when the
                 # main thread exits
    """
    def decorator(func):
        # Whether to continue calling the function
        is_running = True

        # Runs the function periodically
        def start(func, *args, **kwargs):
            while is_running:
                # Call the function
                func(*args, **kwargs)
                # Wait the specified delay before calling again
                time.sleep(delay_secs)

        # Stop calling the function and stop the thread
        def stop():
            is_running = False
            super(ExcThread, self).join()

        # The decorating function
        @wraps(func)
        def async_func(*args, **kwargs):
            # Create the thread
            func_hl = ExcThread(target=partial(start, func), args=args, kwargs=kwargs)
            # If in daemon mode, kill this thread automatically when the main thread exits
            func_hl.daemon = daemon_mode
            # Stop calling the function before waiting otherwise it will never exit
            func_hl.join = types.MethodType(stop, func_hl)
            # Start the thread
            func_hl.start()

            # "async_func" returns the thread reference
            return func_hl

        # "decorator" returns the decorated function
        return async_func

    # "run_async_interval" returns the decorator
    return decorator

def synchronized(my_lock):
    """
    Function decorator, wraps a function in the mutex my_lock
    Eg:
    my_lock = Lock()

    @synchronized(my_lock)
    def task1():
        do_something

    @synchronized(my_lock)
    def task2():
        do_something_else
    """

    def wrap(func):
        def synched_func(*args, **kwargs):
            my_lock.acquire()
            try:
                return func(*args, **kwargs)
            finally:
                my_lock.release()
        return synched_func
    return wrap
