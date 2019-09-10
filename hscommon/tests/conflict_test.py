# Created By: Virgil Dupras
# Created On: 2008-01-08
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.gnu.org/licenses/gpl-3.0.html

from ..conflict import *
from ..path import Path
from ..testutil import eq_

class TestCase_GetConflictedName:
    def test_simple(self):
        name = get_conflicted_name(['bar'], 'bar')
        eq_('[000] bar', name)
        name = get_conflicted_name(['bar', '[000] bar'], 'bar')
        eq_('[001] bar', name)
    
    def test_no_conflict(self):
        name = get_conflicted_name(['bar'], 'foobar')
        eq_('foobar', name)
    
    def test_fourth_digit(self):
        # This test is long because every time we have to add a conflicted name,
        # a test must be made for every other conflicted name existing...
        # Anyway, this has very few chances to happen.
        names = ['bar'] + ['[%03d] bar' % i for i in range(1000)]
        name = get_conflicted_name(names, 'bar')
        eq_('[1000] bar', name)
    
    def test_auto_unconflict(self):
        # Automatically unconflict the name if it's already conflicted.
        name = get_conflicted_name([], '[000] foobar')
        eq_('foobar', name)
        name = get_conflicted_name(['bar'], '[001] bar')
        eq_('[000] bar', name)
    

class TestCase_GetUnconflictedName:
    def test_main(self):
        eq_('foobar',get_unconflicted_name('[000] foobar'))
        eq_('foobar',get_unconflicted_name('[9999] foobar'))
        eq_('[000]foobar',get_unconflicted_name('[000]foobar'))
        eq_('[000a] foobar',get_unconflicted_name('[000a] foobar'))
        eq_('foobar',get_unconflicted_name('foobar'))
        eq_('foo [000] bar',get_unconflicted_name('foo [000] bar'))
    

class TestCase_IsConflicted:
    def test_main(self):
        assert is_conflicted('[000] foobar')
        assert is_conflicted('[9999] foobar')
        assert not is_conflicted('[000]foobar')
        assert not is_conflicted('[000a] foobar')
        assert not is_conflicted('foobar')
        assert not is_conflicted('foo [000] bar')
    

class TestCase_move_copy:
    def pytest_funcarg__do_setup(self, request):
        tmpdir = request.getfuncargvalue('tmpdir')
        self.path = Path(str(tmpdir))
        self.path['foo'].open('w').close()
        self.path['bar'].open('w').close()
        self.path['dir'].mkdir()
    
    def test_move_no_conflict(self, do_setup):
        smart_move(self.path + 'foo', self.path + 'baz')
        assert self.path['baz'].exists()
        assert not self.path['foo'].exists()
    
    def test_copy_no_conflict(self, do_setup): # No need to duplicate the rest of the tests... Let's just test on move
        smart_copy(self.path + 'foo', self.path + 'baz')
        assert self.path['baz'].exists()
        assert self.path['foo'].exists()
    
    def test_move_no_conflict_dest_is_dir(self, do_setup):
        smart_move(self.path + 'foo', self.path + 'dir')
        assert self.path['dir']['foo'].exists()
        assert not self.path['foo'].exists()
    
    def test_move_conflict(self, do_setup):
        smart_move(self.path + 'foo', self.path + 'bar')
        assert self.path['[000] bar'].exists()
        assert not self.path['foo'].exists()
    
    def test_move_conflict_dest_is_dir(self, do_setup):
        smart_move(self.path['foo'], self.path['dir'])
        smart_move(self.path['bar'], self.path['foo'])
        smart_move(self.path['foo'], self.path['dir'])
        assert self.path['dir']['foo'].exists()
        assert self.path['dir']['[000] foo'].exists()
        assert not self.path['foo'].exists()
        assert not self.path['bar'].exists()
    
    def test_copy_folder(self, tmpdir):
        # smart_copy also works on folders
        path = Path(str(tmpdir))
        path['foo'].mkdir()
        path['bar'].mkdir()
        smart_copy(path['foo'], path['bar']) # no crash
        assert path['[000] bar'].exists()
    
