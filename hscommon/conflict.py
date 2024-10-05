# Created By: Virgil Dupras
# Created On: 2008-01-08
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

"""When you have to deal with names that have to be unique and can conflict together, you can use
this module that deals with conflicts by prepending unique numbers in ``[]`` brackets to the name.
"""

import re
import os
import shutil

from errno import EISDIR, EACCES
from pathlib import Path
from typing import Callable, List

# This matches [123], but not [12] (3 digits being the minimum).
# It also matches [1234] [12345] etc..
# And only at the start of the string
re_conflict = re.compile(r"^\[\d{3}\d*\] ")


def get_conflicted_name(other_names: List[str], name: str) -> str:
    """Returns name with a ``[000]`` number in front of it.

    The number between brackets depends on how many conlicted filenames
    there already are in other_names.
    """
    name = get_unconflicted_name(name)
    if name not in other_names:
        return name
    i = 0
    while True:
        newname = "[%03d] %s" % (i, name)
        if newname not in other_names:
            return newname
        i += 1


def get_unconflicted_name(name: str) -> str:
    """Returns ``name`` without ``[]`` brackets.

    Brackets which, of course, might have been added by func:`get_conflicted_name`.
    """
    return re_conflict.sub("", name, 1)


def is_conflicted(name: str) -> bool:
    """Returns whether ``name`` is prepended with a bracketed number."""
    return re_conflict.match(name) is not None


def _smart_move_or_copy(operation: Callable, source_path: Path, dest_path: Path) -> None:
    """Use move() or copy() to move and copy file with the conflict management."""
    if dest_path.is_dir() and not source_path.is_dir():
        dest_path = dest_path.joinpath(source_path.name)
    if dest_path.exists():
        filename = dest_path.name
        dest_dir_path = dest_path.parent
        newname = get_conflicted_name(os.listdir(str(dest_dir_path)), filename)
        dest_path = dest_dir_path.joinpath(newname)
    operation(str(source_path), str(dest_path))


def smart_move(source_path: Path, dest_path: Path) -> None:
    """Same as :func:`smart_copy`, but it moves files instead."""
    _smart_move_or_copy(shutil.move, source_path, dest_path)


def smart_copy(source_path: Path, dest_path: Path) -> None:
    """Copies ``source_path`` to ``dest_path``, recursively and with conflict resolution."""
    try:
        _smart_move_or_copy(shutil.copy, source_path, dest_path)
    except OSError as e:
        # It's a directory, code is 21 on OS X / Linux (EISDIR) and 13 on Windows (EACCES)
        if e.errno in (EISDIR, EACCES):
            _smart_move_or_copy(shutil.copytree, source_path, dest_path)
        else:
            raise
