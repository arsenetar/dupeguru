# Created By: Virgil Dupras
# Created On: 2006/02/21
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from ..path import pathify
from pathlib import Path


def test_pathify():
    @pathify
    def foo(a: Path, b, c: Path):
        return a, b, c

    a, b, c = foo("foo", 0, c=Path("bar"))
    assert isinstance(a, Path)
    assert a == Path("foo")
    assert b == 0
    assert isinstance(c, Path)
    assert c == Path("bar")


def test_pathify_preserve_none():
    # @pathify preserves None value and doesn't try to return a Path
    @pathify
    def foo(a: Path):
        return a

    a = foo(None)
    assert a is None
