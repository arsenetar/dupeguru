# Created By: Virgil Dupras
# Created On: 2010-11-14
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.gnu.org/licenses/gpl-3.0.html

import threading
import py.path

def eq_(a, b, msg=None):
    __tracebackhide__ = True
    assert a == b, msg or "%r != %r" % (a, b)

def assert_almost_equal(a, b, places=7):
    __tracebackhide__ = True
    assert round(a, ndigits=places) == round(b, ndigits=places)

def callcounter():
    def f(*args, **kwargs):
        f.callcount += 1
    
    f.callcount = 0
    return f

class TestData:
    def __init__(self, datadirpath):
        self.datadirpath = py.path.local(datadirpath)
    
    def filepath(self, relative_path, *args):
        """Returns the path of a file in testdata.
        
        'relative_path' can be anything that can be added to a Path
        if args is not empty, it will be joined to relative_path
        """
        resultpath = self.datadirpath.join(relative_path)
        if args:
            resultpath = resultpath.join(*args)
        assert resultpath.check()
        return str(resultpath)
    

class CallLogger:
    """This is a dummy object that logs all calls made to it.
    
    It is used to simulate the GUI layer.
    """
    def __init__(self):
        self.calls = []
    
    def __getattr__(self, func_name):
        def func(*args, **kw):
            self.calls.append(func_name)
        return func
    
    def clear_calls(self):
        del self.calls[:]
    
    def check_gui_calls(self, expected, verify_order=False):
        """Checks that the expected calls have been made to 'self', then clears the log.
        
        `expected` is an iterable of strings representing method names.
        If `verify_order` is True, the order of the calls matters.
        """
        __tracebackhide__ = True
        if verify_order:
            eq_(self.calls, expected)
        else:
            eq_(set(self.calls), set(expected))
        self.clear_calls()
    
    def check_gui_calls_partial(self, expected=None, not_expected=None, verify_order=False):
        """Checks that the expected calls have been made to 'self', then clears the log.
        
        `expected` is an iterable of strings representing method names. Order doesn't matter.
        Moreover, if calls have been made that are not in expected, no failure occur.
        `not_expected` can be used for a more explicit check (rather than calling `check_gui_calls`
        with an empty `expected`) to assert that calls have *not* been made.
        """
        __tracebackhide__ = True
        if expected is not None:
            not_called = set(expected) - set(self.calls)
            assert not not_called, "These calls haven't been made: {0}".format(not_called)
            if verify_order:
                max_index = 0
                for call in expected:
                    index = self.calls.index(call)
                    if index < max_index:
                        raise AssertionError("The call {0} hasn't been made in the correct order".format(call))
                    max_index = index
        if not_expected is not None:
            called = set(not_expected) & set(self.calls)
            assert not called, "These calls shouldn't have been made: {0}".format(called)
        self.clear_calls()
    

class TestApp:
    def __init__(self):
        self._call_loggers = []
    
    def clear_gui_calls(self):
        for logger in self._call_loggers:
            logger.clear_calls()
    
    def make_logger(self, class_=CallLogger, *initargs):
        logger = class_(*initargs)
        self._call_loggers.append(logger)
        return logger
    
    def make_gui(self, name, class_, view=None, parent=None, holder=None):
        if view is None:
            view = self.make_logger()
        if parent is None:
            # The attribute "default_parent" has to be set for this to work correctly
            parent = self.default_parent
        if holder is None:
            holder = self
        setattr(holder, '{0}_gui'.format(name), view)
        gui = class_(parent)
        gui.view = view
        setattr(holder, name, gui)
        return gui
    

# To use @with_app, you have to import pytest_funcarg__app in your conftest.py file.
def with_app(setupfunc):
    def decorator(func):
        func.setupfunc = setupfunc
        return func
    return decorator

def pytest_funcarg__app(request):
    setupfunc = request.function.setupfunc
    if hasattr(setupfunc, '__code__'):
        argnames = setupfunc.__code__.co_varnames[:setupfunc.__code__.co_argcount]
        def getarg(name):
            if name == 'self':
                return request.function.__self__
            else:
                return request.getfuncargvalue(name)
        args = [getarg(argname) for argname in argnames]
    else:
        args = []
    app = setupfunc(*args)
    return app

def jointhreads():
    """Join all threads to the main thread"""
    for thread in threading.enumerate():
        if hasattr(thread, 'BUGGY'):
            continue
        if thread.getName() != 'MainThread' and thread.isAlive():
            if hasattr(thread, 'close'):
                thread.close()
            thread.join(1)
            if thread.isAlive():
                print("Thread problem. Some thread doesn't want to stop.")
                thread.BUGGY = True

def _unify_args(func, args, kwargs, args_to_ignore=None):
    ''' Unify args and kwargs in the same dictionary.
    
        The result is kwargs with args added to it. func.func_code.co_varnames is used to determine
        under what key each elements of arg will be mapped in kwargs.
        
        if you want some arguments not to be in the results, supply a list of arg names in 
        args_to_ignore.
        
        if f is a function that takes *args, func_code.co_varnames is empty, so args will be put 
        under 'args' in kwargs.
        
        def foo(bar, baz)
        _unifyArgs(foo, (42,), {'baz': 23}) --> {'bar': 42, 'baz': 23}
        _unifyArgs(foo, (42,), {'baz': 23}, ['bar']) --> {'baz': 23}
    '''
    result = kwargs.copy()
    if hasattr(func, '__code__'): # built-in functions don't have func_code
        args = list(args)
        if getattr(func, '__self__', None) is not None: # bound method, we have to add self to args list
            args = [func.__self__] + args
        defaults = list(func.__defaults__) if func.__defaults__ is not None else []
        arg_count = func.__code__.co_argcount
        arg_names = list(func.__code__.co_varnames)
        if len(args) < arg_count: # We have default values
            required_arg_count = arg_count - len(args)
            args = args + defaults[-required_arg_count:]
        for arg_name, arg in zip(arg_names, args):
            # setdefault is used because if the arg is already in kwargs, we don't want to use default values
            result.setdefault(arg_name, arg)
    else:
        #'func' has a *args argument
        result['args'] = args
    if args_to_ignore:
        for kw in args_to_ignore:
            del result[kw]
    return result

def log_calls(func):
    ''' Logs all func calls' arguments under func.calls.
    
        func.calls is a list of _unify_args() result (dict).
        
        Mostly used for unit testing.
    '''
    def wrapper(*args, **kwargs):
        unifiedArgs = _unify_args(func, args, kwargs)
        wrapper.calls.append(unifiedArgs)
        return func(*args, **kwargs)
    
    wrapper.calls = []
    return wrapper
