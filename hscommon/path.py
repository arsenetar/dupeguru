# Created By: Virgil Dupras
# Created On: 2006/02/21
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

import logging
from functools import wraps
from inspect import signature
from pathlib import Path


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
    """Catches OSError, IOError and WindowsError and log them"""

    @wraps(func)
    def wrapper(path, *args, **kwargs):
        try:
            return func(path, *args, **kwargs)
        except (IOError, OSError) as e:
            msg = 'Error "{0}" during operation "{1}" on "{2}": "{3}"'
            classname = e.__class__.__name__
            funcname = func.__name__
            logging.warning(msg.format(classname, funcname, str(path), str(e)))

    return wrapper
