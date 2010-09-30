# Created By: Virgil Dupras
# Created On: 2007-06-23
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import os
import logging

from hsutil.testutil import eq_
from hsutil.testcase import TestCase
from hsutil import io
from hsutil.path import Path
from hsutil.decorators import log_calls
import hsutil.files
from hscommon.job import nulljob

from . import data
from .results_test import GetTestGroups
from .. import app, fs, engine
from ..app import DupeGuru as DupeGuruBase
from ..gui.details_panel import DetailsPanel
from ..gui.directory_tree import DirectoryTree
from ..gui.result_table import ResultTable
from ..scanner import ScanType

class DupeGuru(DupeGuruBase):
    def __init__(self):
        DupeGuruBase.__init__(self, data, '/tmp', appid=4)
    
    def _start_job(self, jobid, func, *args):
        func(nulljob, *args)
    

class CallLogger(object):
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
    

class TCDupeGuru(TestCase):
    cls_tested_module = app
    def test_apply_filter_calls_results_apply_filter(self):
        app = DupeGuru()
        self.mock(app.results, 'apply_filter', log_calls(app.results.apply_filter))
        app.apply_filter('foo')
        self.assertEqual(2, len(app.results.apply_filter.calls))
        call = app.results.apply_filter.calls[0]
        self.assert_(call['filter_str'] is None)
        call = app.results.apply_filter.calls[1]
        self.assertEqual('foo', call['filter_str'])
    
    def test_apply_filter_escapes_regexp(self):
        app = DupeGuru()
        self.mock(app.results, 'apply_filter', log_calls(app.results.apply_filter))
        app.apply_filter('()[]\\.|+?^abc')
        call = app.results.apply_filter.calls[1]
        self.assertEqual('\\(\\)\\[\\]\\\\\\.\\|\\+\\?\\^abc', call['filter_str'])
        app.apply_filter('(*)') # In "simple mode", we want the * to behave as a wilcard
        call = app.results.apply_filter.calls[3]
        self.assertEqual('\(.*\)', call['filter_str'])
        app.options['escape_filter_regexp'] = False
        app.apply_filter('(abc)')
        call = app.results.apply_filter.calls[5]
        self.assertEqual('(abc)', call['filter_str'])
    
    def test_copy_or_move(self):
        # The goal here is just to have a test for a previous blowup I had. I know my test coverage
        # for this unit is pathetic. What's done is done. My approach now is to add tests for
        # every change I want to make. The blowup was caused by a missing import.
        p = self.tmppath()
        io.open(p + 'foo', 'w').close()
        self.mock(hsutil.files, 'copy', log_calls(lambda source_path, dest_path: None))
        self.mock(os, 'makedirs', lambda path: None) # We don't want the test to create that fake directory
        app = DupeGuru()
        app.directories.add_path(p)
        [f] = app.directories.get_files()
        app.copy_or_move(f, True, 'some_destination', 0)
        self.assertEqual(1, len(hsutil.files.copy.calls))
        call = hsutil.files.copy.calls[0]
        self.assertEqual('some_destination', call['dest_path'])
        self.assertEqual(f.path, call['source_path'])
    
    def test_copy_or_move_clean_empty_dirs(self):
        tmppath = Path(self.tmpdir())
        sourcepath = tmppath + 'source'
        io.mkdir(sourcepath)
        io.open(sourcepath + 'myfile', 'w')
        app = DupeGuru()
        app.directories.add_path(tmppath)
        [myfile] = app.directories.get_files()
        self.mock(app, 'clean_empty_dirs', log_calls(lambda path: None))
        app.copy_or_move(myfile, False, tmppath + 'dest', 0)
        calls = app.clean_empty_dirs.calls
        self.assertEqual(1, len(calls))
        self.assertEqual(sourcepath, calls[0]['path'])
    
    def test_Scan_with_objects_evaluating_to_false(self):
        class FakeFile(fs.File):
            def __bool__(self):
                return False
            
        
        # At some point, any() was used in a wrong way that made Scan() wrongly return 1
        app = DupeGuru()
        f1, f2 = [FakeFile('foo') for i in range(2)]
        f1.is_ref, f2.is_ref = (False, False)
        assert not (bool(f1) and bool(f2))
        app.directories.get_files = lambda: iter([f1, f2])
        app.directories._dirs.append('this is just so Scan() doesnt return 3')
        app.start_scanning() # no exception
    
    def test_ignore_hardlink_matches(self):
        # If the ignore_hardlink_matches option is set, don't match files hardlinking to the same
        # inode.
        tmppath = Path(self.tmpdir())
        io.open(tmppath + 'myfile', 'w').write('foo')
        os.link(str(tmppath + 'myfile'), str(tmppath + 'hardlink'))
        app = DupeGuru()
        app.directories.add_path(tmppath)
        app.scanner.scan_type = ScanType.Contents
        app.options['ignore_hardlink_matches'] = True
        app.start_scanning()
        eq_(len(app.results.groups), 0)
    

class TCDupeGuru_clean_empty_dirs(TestCase):
    cls_tested_module = app
    def setUp(self):
        self.mock(hsutil.files, 'delete_if_empty', log_calls(lambda path, files_to_delete=[]: None))
        self.app = DupeGuru()
    
    def test_option_off(self):
        self.app.clean_empty_dirs(Path('/foo/bar'))
        self.assertEqual(0, len(hsutil.files.delete_if_empty.calls))
    
    def test_option_on(self):
        self.app.options['clean_empty_dirs'] = True
        self.app.clean_empty_dirs(Path('/foo/bar'))
        calls = hsutil.files.delete_if_empty.calls
        self.assertEqual(1, len(calls))
        self.assertEqual(Path('/foo/bar'), calls[0]['path'])
        self.assertEqual(['.DS_Store'], calls[0]['files_to_delete'])
    
    def test_recurse_up(self):
        # delete_if_empty must be recursively called up in the path until it returns False
        @log_calls
        def mock_delete_if_empty(path, files_to_delete=[]):
            return len(path) > 1
        
        self.mock(hsutil.files, 'delete_if_empty', mock_delete_if_empty)
        self.app.options['clean_empty_dirs'] = True
        self.app.clean_empty_dirs(Path('not-empty/empty/empty'))
        calls = hsutil.files.delete_if_empty.calls
        self.assertEqual(3, len(calls))
        self.assertEqual(Path('not-empty/empty/empty'), calls[0]['path'])
        self.assertEqual(Path('not-empty/empty'), calls[1]['path'])
        self.assertEqual(Path('not-empty'), calls[2]['path'])
    

class TCDupeGuruWithResults(TestCase):
    def setUp(self):
        self.app = DupeGuru()
        self.objects,self.matches,self.groups = GetTestGroups()
        self.app.results.groups = self.groups
        self.dpanel_gui = CallLogger()
        self.dpanel = DetailsPanel(self.dpanel_gui, self.app)
        self.dtree_gui = CallLogger()
        self.dtree = DirectoryTree(self.dtree_gui, self.app)
        self.rtable_gui = CallLogger()
        self.rtable = ResultTable(self.rtable_gui, self.app)
        self.dpanel.connect()
        self.dtree.connect()
        self.rtable.connect()
        tmppath = self.tmppath()
        io.mkdir(tmppath + 'foo')
        io.mkdir(tmppath + 'bar')
        self.app.directories.add_path(tmppath)
    
    def check_gui_calls(self, gui, expected, verify_order=False):
        """Checks that the expected calls have been made to 'gui', then clears the log.
        
        `expected` is an iterable of strings representing method names.
        If `verify_order` is True, the order of the calls matters.
        """
        if verify_order:
            eq_(gui.calls, expected)
        else:
            eq_(set(gui.calls), set(expected))
        gui.clear_calls()
    
    def check_gui_calls_partial(self, gui, expected=None, not_expected=None):
        """Checks that the expected calls have been made to 'gui', then clears the log.
        
        `expected` is an iterable of strings representing method names. Order doesn't matter.
        Moreover, if calls have been made that are not in expected, no failure occur.
        `not_expected` can be used for a more explicit check (rather than calling `check_gui_calls`
        with an empty `expected`) to assert that calls have *not* been made.
        """
        calls = set(gui.calls)
        if expected is not None:
            expected = set(expected)
            not_called = expected - calls
            assert not not_called, "These calls haven't been made: {0}".format(not_called)
        if not_expected is not None:
            not_expected = set(not_expected)
            called = not_expected & calls
            assert not called, "These calls shouldn't have been made: {0}".format(called)
        gui.clear_calls()
    
    def clear_gui_calls(self):
        for attr in dir(self):
            if attr.endswith('_gui'):
                gui = getattr(self, attr)
                if hasattr(gui, 'calls'): # We might have test methods ending with '_gui'
                    gui.clear_calls()
    
    def test_GetObjects(self):
        objects = self.objects
        groups = self.groups
        r = self.rtable[0]
        assert r._group is groups[0]
        assert r._dupe is objects[0]
        r = self.rtable[1]
        assert r._group is groups[0]
        assert r._dupe is objects[1]
        r = self.rtable[4]
        assert r._group is groups[1]
        assert r._dupe is objects[4]
    
    def test_GetObjects_after_sort(self):
        objects = self.objects
        groups = self.groups[:] # we need an un-sorted reference
        self.rtable.sort(0, False) #0 = Filename
        r = self.rtable[1]
        assert r._group is groups[1]
        assert r._dupe is objects[4]
    
    def test_selected_result_node_paths_after_deletion(self):
        # cases where the selected dupes aren't there are correctly handled
        self.rtable.select([1, 2, 3])
        self.app.remove_selected()
        # The first 2 dupes have been removed. The 3rd one is a ref. it stays there, in first pos.
        eq_(self.rtable.selected_indexes, [1]) # no exception
    
    def test_selectResultNodePaths(self):
        app = self.app
        objects = self.objects
        self.rtable.select([1, 2])
        eq_(len(app.selected_dupes), 2)
        assert app.selected_dupes[0] is objects[1]
        assert app.selected_dupes[1] is objects[2]
    
    def test_selectResultNodePaths_with_ref(self):
        app = self.app
        objects = self.objects
        self.rtable.select([1, 2, 3])
        eq_(len(app.selected_dupes), 3)
        assert app.selected_dupes[0] is objects[1]
        assert app.selected_dupes[1] is objects[2]
        assert app.selected_dupes[2] is self.groups[1].ref
    
    def test_selectResultNodePaths_after_sort(self):
        app = self.app
        objects = self.objects
        groups = self.groups[:] #To keep the old order in memory
        self.rtable.sort(0, False) #0 = Filename
        #Now, the group order is supposed to be reversed
        self.rtable.select([1, 2, 3])
        eq_(len(app.selected_dupes), 3)
        assert app.selected_dupes[0] is objects[4]
        assert app.selected_dupes[1] is groups[0].ref
        assert app.selected_dupes[2] is objects[1]
    
    def test_selected_powermarker_node_paths(self):
        # app.selected_dupes is correctly converted into paths
        app = self.app
        objects = self.objects
        self.rtable.power_marker = True
        self.rtable.select([0, 1, 2])
        self.rtable.power_marker = False
        eq_(self.rtable.selected_indexes, [1, 2, 4])
    
    def test_selected_powermarker_node_paths_after_deletion(self):
        # cases where the selected dupes aren't there are correctly handled
        app = self.app
        objects = self.objects
        self.rtable.power_marker = True
        self.rtable.select([0, 1, 2])
        app.remove_selected()
        eq_(self.rtable.selected_indexes, []) # no exception
    
    def test_selectPowerMarkerRows_after_sort(self):
        app = self.app
        objects = self.objects
        self.rtable.power_marker = True
        self.rtable.sort(0, False) #0 = Filename
        self.rtable.select([0, 1, 2])
        eq_(len(app.selected_dupes), 3)
        assert app.selected_dupes[0] is objects[4]
        assert app.selected_dupes[1] is objects[2]
        assert app.selected_dupes[2] is objects[1]
    
    def test_toggleSelectedMark(self):
        app = self.app
        objects = self.objects
        app.toggle_selected_mark_state()
        eq_(app.results.mark_count, 0)
        self.rtable.select([1, 4])
        app.toggle_selected_mark_state()
        eq_(app.results.mark_count, 2)
        assert not app.results.is_marked(objects[0])
        assert app.results.is_marked(objects[1])
        assert not app.results.is_marked(objects[2])
        assert not app.results.is_marked(objects[3])
        assert app.results.is_marked(objects[4])
    
    def test_refreshDetailsWithSelected(self):
        self.rtable.select([1, 4])
        eq_(self.dpanel.row(0), ('Filename', 'bar bleh', 'foo bar'))
        self.check_gui_calls(self.dpanel_gui, ['refresh'])
        self.rtable.select([])
        eq_(self.dpanel.row(0), ('Filename', '---', '---'))
        self.check_gui_calls(self.dpanel_gui, ['refresh'])
    
    def test_makeSelectedReference(self):
        app = self.app
        objects = self.objects
        groups = self.groups
        self.rtable.select([1, 4])
        app.make_selected_reference()
        assert groups[0].ref is objects[1]
        assert groups[1].ref is objects[4]
    
    def test_makeSelectedReference_by_selecting_two_dupes_in_the_same_group(self):
        app = self.app
        objects = self.objects
        groups = self.groups
        self.rtable.select([1, 2, 4])
        #Only [0, 0] and [1, 0] must go ref, not [0, 1] because it is a part of the same group
        app.make_selected_reference()
        assert groups[0].ref is objects[1]
        assert groups[1].ref is objects[4]
    
    def test_removeSelected(self):
        app = self.app
        self.rtable.select([1, 4])
        app.remove_selected()
        eq_(len(app.results.dupes), 1) # the first path is now selected
        app.remove_selected()
        eq_(len(app.results.dupes), 0)
    
    def test_addDirectory_simple(self):
        # There's already a directory in self.app, so adding another once makes 2 of em
        app = self.app
        eq_(app.add_directory(self.datadirpath()), 0)
        eq_(len(app.directories), 2)
    
    def test_addDirectory_already_there(self):
        app = self.app
        self.assertEqual(0,app.add_directory(self.datadirpath()))
        self.assertEqual(1,app.add_directory(self.datadirpath()))
    
    def test_addDirectory_does_not_exist(self):
        app = self.app
        self.assertEqual(2,app.add_directory('/does_not_exist'))
    
    def test_ignore(self):
        app = self.app
        self.rtable.select([4]) #The dupe of the second, 2 sized group
        app.add_selected_to_ignore_list()
        eq_(len(app.scanner.ignore_list), 1)
        self.rtable.select([1]) #first dupe of the 3 dupes group
        app.add_selected_to_ignore_list()
        #BOTH the ref and the other dupe should have been added
        eq_(len(app.scanner.ignore_list), 3)
    
    def test_purgeIgnoreList(self):
        app = self.app
        p1 = self.filepath('zerofile')
        p2 = self.filepath('zerofill')
        dne = '/does_not_exist'
        app.scanner.ignore_list.Ignore(dne,p1)
        app.scanner.ignore_list.Ignore(p2,dne)
        app.scanner.ignore_list.Ignore(p1,p2)
        app.purge_ignore_list()
        self.assertEqual(1,len(app.scanner.ignore_list))
        self.assert_(app.scanner.ignore_list.AreIgnored(p1,p2))
        self.assert_(not app.scanner.ignore_list.AreIgnored(dne,p1))
    
    def test_only_unicode_is_added_to_ignore_list(self):
        def FakeIgnore(first,second):
            if not isinstance(first,str):
                self.fail()
            if not isinstance(second,str):
                self.fail()
        
        app = self.app
        app.scanner.ignore_list.Ignore = FakeIgnore
        self.rtable.select([4])
        app.add_selected_to_ignore_list()
    

class TCDupeGuru_renameSelected(TestCase):
    def setUp(self):
        p = self.tmppath()
        fp = open(str(p + 'foo bar 1'),mode='w')
        fp.close()
        fp = open(str(p + 'foo bar 2'),mode='w')
        fp.close()
        fp = open(str(p + 'foo bar 3'),mode='w')
        fp.close()
        files = fs.get_files(p)
        matches = engine.getmatches(files)
        groups = engine.get_groups(matches)
        g = groups[0]
        g.prioritize(lambda x:x.name)
        app = DupeGuru()
        app.results.groups = groups
        self.app = app
        self.groups = groups
        self.p = p
        self.files = files
        self.rtable_gui = CallLogger()
        self.rtable = ResultTable(self.rtable_gui, self.app)
        self.rtable.connect()
    
    def test_simple(self):
        app = self.app
        g = self.groups[0]
        self.rtable.select([1])
        assert app.rename_selected('renamed')
        names = io.listdir(self.p)
        assert 'renamed' in names
        assert 'foo bar 2' not in names
        eq_(g.dupes[0].name, 'renamed')
    
    def test_none_selected(self):
        app = self.app
        g = self.groups[0]
        self.rtable.select([])
        self.mock(logging, 'warning', log_calls(lambda msg: None))
        assert not app.rename_selected('renamed')
        msg = logging.warning.calls[0]['msg']
        eq_('dupeGuru Warning: list index out of range', msg)
        names = io.listdir(self.p)
        assert 'renamed' not in names
        assert 'foo bar 2' in names
        eq_(g.dupes[0].name, 'foo bar 2')
    
    def test_name_already_exists(self):
        app = self.app
        g = self.groups[0]
        self.rtable.select([1])
        self.mock(logging, 'warning', log_calls(lambda msg: None))
        assert not app.rename_selected('foo bar 1')
        msg = logging.warning.calls[0]['msg']
        assert msg.startswith('dupeGuru Warning: \'foo bar 1\' already exists in')
        names = io.listdir(self.p)
        assert 'foo bar 1' in names
        assert 'foo bar 2' in names
        eq_(g.dupes[0].name, 'foo bar 2')
    
