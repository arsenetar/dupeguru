# Copyright 2016 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from hscommon.testutil import eq_

from ..markable import MarkableList, Markable


def gen():
    ml = MarkableList()
    ml.extend(list(range(10)))
    return ml


def test_unmarked():
    ml = gen()
    for i in ml:
        assert not ml.is_marked(i)


def test_mark():
    ml = gen()
    assert ml.mark(3)
    assert ml.is_marked(3)
    assert not ml.is_marked(2)


def test_unmark():
    ml = gen()
    ml.mark(4)
    assert ml.unmark(4)
    assert not ml.is_marked(4)


def test_unmark_unmarked():
    ml = gen()
    assert not ml.unmark(4)
    assert not ml.is_marked(4)


def test_mark_twice_and_unmark():
    ml = gen()
    assert ml.mark(5)
    assert not ml.mark(5)
    ml.unmark(5)
    assert not ml.is_marked(5)


def test_mark_toggle():
    ml = gen()
    ml.mark_toggle(6)
    assert ml.is_marked(6)
    ml.mark_toggle(6)
    assert not ml.is_marked(6)
    ml.mark_toggle(6)
    assert ml.is_marked(6)


def test_is_markable():
    class Foobar(Markable):
        def _is_markable(self, o):
            return o == "foobar"

    f = Foobar()
    assert not f.is_marked("foobar")
    assert not f.mark("foo")
    assert not f.is_marked("foo")
    f.mark_toggle("foo")
    assert not f.is_marked("foo")
    f.mark("foobar")
    assert f.is_marked("foobar")
    ml = gen()
    ml.mark(11)
    assert not ml.is_marked(11)


def test_change_notifications():
    class Foobar(Markable):
        def _did_mark(self, o):
            self.log.append((True, o))

        def _did_unmark(self, o):
            self.log.append((False, o))

    f = Foobar()
    f.log = []
    f.mark("foo")
    f.mark("foo")
    f.mark_toggle("bar")
    f.unmark("foo")
    f.unmark("foo")
    f.mark_toggle("bar")
    eq_([(True, "foo"), (True, "bar"), (False, "foo"), (False, "bar")], f.log)


def test_mark_count():
    ml = gen()
    eq_(0, ml.mark_count)
    ml.mark(7)
    eq_(1, ml.mark_count)
    ml.mark(11)
    eq_(1, ml.mark_count)


def test_mark_none():
    log = []
    ml = gen()
    ml._did_unmark = lambda o: log.append(o)
    ml.mark(1)
    ml.mark(2)
    eq_(2, ml.mark_count)
    ml.mark_none()
    eq_(0, ml.mark_count)
    eq_([1, 2], log)


def test_mark_all():
    ml = gen()
    eq_(0, ml.mark_count)
    ml.mark_all()
    eq_(10, ml.mark_count)
    assert ml.is_marked(1)


def test_mark_invert():
    ml = gen()
    ml.mark(1)
    ml.mark_invert()
    assert not ml.is_marked(1)
    assert ml.is_marked(2)


def test_mark_while_inverted():
    log = []
    ml = gen()
    ml._did_unmark = lambda o: log.append((False, o))
    ml._did_mark = lambda o: log.append((True, o))
    ml.mark(1)
    ml.mark_invert()
    assert ml.mark_inverted
    assert ml.mark(1)
    assert ml.unmark(2)
    assert ml.unmark(1)
    ml.mark_toggle(3)
    assert not ml.is_marked(3)
    eq_(7, ml.mark_count)
    eq_([(True, 1), (False, 1), (True, 2), (True, 1), (True, 3)], log)


def test_remove_mark_flag():
    ml = gen()
    ml.mark(1)
    ml._remove_mark_flag(1)
    assert not ml.is_marked(1)
    ml.mark(1)
    ml.mark_invert()
    assert not ml.is_marked(1)
    ml._remove_mark_flag(1)
    assert ml.is_marked(1)


def test_is_marked_returns_false_if_object_not_markable():
    class MyMarkableList(MarkableList):
        def _is_markable(self, o):
            return o != 4

    ml = MyMarkableList()
    ml.extend(list(range(10)))
    ml.mark_invert()
    assert ml.is_marked(1)
    assert not ml.is_marked(4)
