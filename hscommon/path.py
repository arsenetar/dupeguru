# Created By: Virgil Dupras
# Created On: 2006/02/21
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.gnu.org/licenses/gpl-3.0.html

import logging
import os
import os.path as op
import shutil
import sys
from itertools import takewhile
from functools import wraps
from inspect import signature

class Path(tuple):
    """A handy class to work with paths.
    
    We subclass ``tuple``, each element of the tuple represents an element of the path.
    
    * ``Path('/foo/bar/baz')[1]`` --> ``'bar'``
    * ``Path('/foo/bar/baz')[1:2]`` --> ``Path('bar/baz')``
    * ``Path('/foo/bar')['baz']`` --> ``Path('/foo/bar/baz')``
    * ``str(Path('/foo/bar/baz'))`` --> ``'/foo/bar/baz'``
    """
    # Saves a little bit of memory usage
    __slots__ = ()
    
    def __new__(cls, value, separator=None):
        def unicode_if_needed(s):
            if isinstance(s, str):
                return s
            else:
                try:
                    return str(s, sys.getfilesystemencoding())
                except UnicodeDecodeError:
                    logging.warning("Could not decode %r", s)
                    raise
        
        if isinstance(value, Path):
            return value
        if not separator:
            separator = os.sep
        if isinstance(value, bytes):
            value = unicode_if_needed(value)
        if isinstance(value, str):
            if value:
                if (separator not in value) and ('/' in value):
                    separator = '/'
                value = value.split(separator)
            else:
                value = ()
        else:
            if any(isinstance(x, bytes) for x in value):
                value = [unicode_if_needed(x) for x in value]
            #value is a tuple/list
            if any(separator in x for x in value):
                #We have a component with a separator in it. Let's rejoin it, and generate another path.
                return Path(separator.join(value), separator)
        if (len(value) > 1) and (not value[-1]):
            value = value[:-1] #We never want a path to end with a '' (because Path() can be called with a trailing slash ending path)
        return tuple.__new__(cls, value)
    
    def __add__(self, other):
        other = Path(other)
        if other and (not other[0]):
            other = other[1:]
        return Path(tuple.__add__(self, other))
    
    def __contains__(self, item):
        if isinstance(item, Path):
            return item[:len(self)] == self
        else:
            return tuple.__contains__(self, item)
    
    def __eq__(self, other):
        return tuple.__eq__(self, Path(other))
    
    def __getitem__(self, key):
        if isinstance(key, slice):
            if isinstance(key.start, Path):
                equal_elems = list(takewhile(lambda pair: pair[0] == pair[1], zip(self, key.start)))
                key = slice(len(equal_elems), key.stop, key.step)
            if isinstance(key.stop, Path):
                equal_elems = list(takewhile(lambda pair: pair[0] == pair[1], zip(reversed(self), reversed(key.stop))))
                stop = -len(equal_elems) if equal_elems else None
                key = slice(key.start, stop, key.step)
            return Path(tuple.__getitem__(self, key))
        elif isinstance(key, (str, Path)):
            return self + key
        else:
            return tuple.__getitem__(self, key)
    
    def __hash__(self):
        return tuple.__hash__(self)
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __radd__(self, other):
        return Path(other) + self
    
    def __str__(self):
        if len(self) == 1:
            first = self[0]
            if (len(first) == 2) and (first[1] == ':'): #Windows drive letter
                return first + '\\'
            elif not len(first): #root directory
                return '/'
        return os.sep.join(self)
    
    def has_drive_letter(self):
        if not self:
            return False
        first = self[0]
        return (len(first) == 2) and (first[1] == ':')
    
    def is_parent_of(self, other):
        """Whether ``other`` is a subpath of ``self``.

        Almost the same as ``other in self``, but it's a bit more self-explicative and when
        ``other == self``, returns False.
        """
        if other == self:
            return False
        else:
            return other in self

    def remove_drive_letter(self):
        if self.has_drive_letter():
            return self[1:]
        else:
            return self
    
    def tobytes(self):
        return str(self).encode(sys.getfilesystemencoding())
    
    def parent(self):
        """Returns the parent path.
        
        ``Path('/foo/bar/baz').parent()`` --> ``Path('/foo/bar')``
        """
        return self[:-1]
    
    @property
    def name(self):
        """Last element of the path (filename), with extension.
        
        ``Path('/foo/bar/baz').name`` --> ``'baz'``
        """
        return self[-1]
    
    # OS method wrappers
    def exists(self):
        return op.exists(str(self))
    
    def copy(self, dest_path):
        return shutil.copy(str(self), str(dest_path))

    def copytree(self, dest_path, *args, **kwargs):
        return shutil.copytree(str(self), str(dest_path), *args, **kwargs)

    def isdir(self):
        return op.isdir(str(self))

    def isfile(self):
        return op.isfile(str(self))

    def islink(self):
        return op.islink(str(self))

    def listdir(self):
        return [self[name] for name in os.listdir(str(self))]

    def mkdir(self, *args, **kwargs):
        return os.mkdir(str(self), *args, **kwargs)

    def makedirs(self, *args, **kwargs):
        return os.makedirs(str(self), *args, **kwargs)

    def move(self, dest_path):
        return shutil.move(str(self), str(dest_path))

    def open(self, *args, **kwargs):
        return open(str(self), *args, **kwargs)

    def remove(self):
        return os.remove(str(self))

    def rename(self, dest_path):
        return os.rename(str(self), str(dest_path))

    def rmdir(self):
        return os.rmdir(str(self))

    def rmtree(self):
        return shutil.rmtree(str(self))

    def stat(self):
        return os.stat(str(self))
    
def pathify(f):
    """Ensure that every annotated :class:`Path` arguments are actually paths.
    
    When a function is decorated with ``@pathify``, every argument with annotated as Path will be
    converted to a Path if it wasn't already. Example::
    
        @pathify
        def foo(path: Path, otherarg):
            return path.listdir()
    
    Calling ``foo('/bar', 0)`` will convert ``'/bar'`` to ``Path('/bar')``.
    """
    sig = signature(f)
    pindexes = {i for i, p in enumerate(sig.parameters.values()) if p.annotation is Path}
    pkeys = {k: v for k, v in sig.parameters.items() if v.annotation is Path}
    def path_or_none(p):
        return None if p is None else Path(p)
    
    @wraps(f)
    def wrapped(*args, **kwargs):
        args = tuple((path_or_none(a) if i in pindexes else a) for i, a in enumerate(args))
        kwargs = {k: (path_or_none(v) if k in pkeys else v) for k, v in kwargs.items()}
        return f(*args, **kwargs)
    
    return wrapped

def log_io_error(func):
    """ Catches OSError, IOError and WindowsError and log them
    """
    @wraps(func)
    def wrapper(path, *args, **kwargs):
        try:
            return func(path, *args, **kwargs)
        except (IOError, OSError) as e:
            msg = 'Error "{0}" during operation "{1}" on "{2}": "{3}"'
            classname = e.__class__.__name__
            funcname = func.__name__
            logging.warn(msg.format(classname, funcname, str(path), str(e)))
    
    return wrapper
