# Created By: Virgil Dupras
# Created On: 2006/11/11
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import tempfile
import shutil
import logging
import os.path as op

from nose.tools import eq_

from hsutil.path import Path
from hsutil.testcase import TestCase
from hsutil.decorators import log_calls
from hsutil import io

from . import data
from .results_test import GetTestGroups
from .. import engine, fs
try:
    from ..app_cocoa import DupeGuru as DupeGuruBase
except ImportError:
    from nose.plugins.skip import SkipTest
    raise SkipTest("These tests can only be run on OS X")

class DupeGuru(DupeGuruBase):
    def __init__(self):
        DupeGuruBase.__init__(self, data, '/tmp', appid=4)
    
    def _start_job(self, jobid, func):
        func(nulljob)
    
def r2np(rows):
    #Transforms a list of rows [1,2,3] into a list of node paths [[1],[2],[3]]
    return [[i] for i in rows]

class TCDupeGuru(TestCase):
    def setUp(self):
        self.app = DupeGuru()
        self.objects,self.matches,self.groups = GetTestGroups()
        self.app.results.groups = self.groups
        tmppath = self.tmppath()
        io.mkdir(tmppath + 'foo')
        io.mkdir(tmppath + 'bar')
        self.app.directories.add_path(tmppath)
    
    def test_GetObjects(self):
        app = self.app
        objects = self.objects
        groups = self.groups
        g,d = app.GetObjects([0])
        self.assert_(g is groups[0])
        self.assert_(d is None)
        g,d = app.GetObjects([0,0])
        self.assert_(g is groups[0])
        self.assert_(d is objects[1])
        g,d = app.GetObjects([1,0])
        self.assert_(g is groups[1])
        self.assert_(d is objects[4])
    
    def test_GetObjects_after_sort(self):
        app = self.app
        objects = self.objects
        groups = self.groups[:] #To keep the old order in memory
        app.sort_groups(0,False) #0 = Filename
        #Now, the group order is supposed to be reversed
        g,d = app.GetObjects([0,0])
        self.assert_(g is groups[1])
        self.assert_(d is objects[4])
    
    def test_GetObjects_out_of_range(self):
        app = self.app
        self.assertEqual((None,None),app.GetObjects([2]))
        self.assertEqual((None,None),app.GetObjects([]))
        self.assertEqual((None,None),app.GetObjects([1,2]))
    
    def test_selected_result_node_paths(self):
        # app.selected_dupes is correctly converted into node paths
        app = self.app
        objects = self.objects
        paths = [[0, 0], [0, 1], [1]]
        app.SelectResultNodePaths(paths)
        eq_(app.selected_result_node_paths(), paths)
    
    def test_selected_result_node_paths_after_deletion(self):
        # cases where the selected dupes aren't there are correctly handled
        app = self.app
        objects = self.objects
        paths = [[0, 0], [0, 1], [1]]
        app.SelectResultNodePaths(paths)
        app.RemoveSelected()
        # The first 2 dupes have been removed. The 3rd one is a ref. it stays there, in first pos.
        eq_(app.selected_result_node_paths(), [[0]]) # no exception
    
    def test_selectResultNodePaths(self):
        app = self.app
        objects = self.objects
        app.SelectResultNodePaths([[0,0],[0,1]])
        self.assertEqual(2,len(app.selected_dupes))
        self.assert_(app.selected_dupes[0] is objects[1])
        self.assert_(app.selected_dupes[1] is objects[2])
    
    def test_selectResultNodePaths_with_ref(self):
        app = self.app
        objects = self.objects
        app.SelectResultNodePaths([[0,0],[0,1],[1]])
        self.assertEqual(3,len(app.selected_dupes))
        self.assert_(app.selected_dupes[0] is objects[1])
        self.assert_(app.selected_dupes[1] is objects[2])
        self.assert_(app.selected_dupes[2] is self.groups[1].ref)
    
    def test_selectResultNodePaths_empty(self):
        self.app.SelectResultNodePaths([])
        self.assertEqual(0,len(self.app.selected_dupes))        
    
    def test_selectResultNodePaths_after_sort(self):
        app = self.app
        objects = self.objects
        groups = self.groups[:] #To keep the old order in memory
        app.sort_groups(0,False) #0 = Filename
        #Now, the group order is supposed to be reversed
        app.SelectResultNodePaths([[0,0],[1],[1,0]])
        self.assertEqual(3,len(app.selected_dupes))
        self.assert_(app.selected_dupes[0] is objects[4])
        self.assert_(app.selected_dupes[1] is groups[0].ref)
        self.assert_(app.selected_dupes[2] is objects[1])
    
    def test_selectResultNodePaths_out_of_range(self):
        app = self.app
        app.SelectResultNodePaths([[0,0],[0,1],[1],[1,1],[2]])
        self.assertEqual(3,len(app.selected_dupes))
    
    def test_selected_powermarker_node_paths(self):
        # app.selected_dupes is correctly converted into paths
        app = self.app
        objects = self.objects
        paths = r2np([0, 1, 2])
        app.SelectPowerMarkerNodePaths(paths)
        eq_(app.selected_powermarker_node_paths(), paths)
    
    def test_selected_powermarker_node_paths_after_deletion(self):
        # cases where the selected dupes aren't there are correctly handled
        app = self.app
        objects = self.objects
        paths = r2np([0, 1, 2])
        app.SelectPowerMarkerNodePaths(paths)
        app.RemoveSelected()
        eq_(app.selected_powermarker_node_paths(), []) # no exception
    
    def test_selectPowerMarkerRows(self):
        app = self.app
        objects = self.objects
        app.SelectPowerMarkerNodePaths(r2np([0,1,2]))
        self.assertEqual(3,len(app.selected_dupes))
        self.assert_(app.selected_dupes[0] is objects[1])
        self.assert_(app.selected_dupes[1] is objects[2])
        self.assert_(app.selected_dupes[2] is objects[4])
    
    def test_selectPowerMarkerRows_empty(self):
        self.app.SelectPowerMarkerNodePaths([])
        self.assertEqual(0,len(self.app.selected_dupes))
    
    def test_selectPowerMarkerRows_after_sort(self):
        app = self.app
        objects = self.objects
        app.sort_dupes(0,False) #0 = Filename
        app.SelectPowerMarkerNodePaths(r2np([0,1,2]))
        self.assertEqual(3,len(app.selected_dupes))
        self.assert_(app.selected_dupes[0] is objects[4])
        self.assert_(app.selected_dupes[1] is objects[2])
        self.assert_(app.selected_dupes[2] is objects[1])
    
    def test_selectPowerMarkerRows_out_of_range(self):
        app = self.app
        app.SelectPowerMarkerNodePaths(r2np([0,1,2,3]))
        self.assertEqual(3,len(app.selected_dupes))
    
    def test_toggleSelectedMark(self):
        app = self.app
        objects = self.objects
        app.ToggleSelectedMarkState()
        self.assertEqual(0,app.results.mark_count)
        app.SelectPowerMarkerNodePaths(r2np([0,2]))
        app.ToggleSelectedMarkState()
        self.assertEqual(2,app.results.mark_count)
        self.assert_(not app.results.is_marked(objects[0]))
        self.assert_(app.results.is_marked(objects[1]))
        self.assert_(not app.results.is_marked(objects[2]))
        self.assert_(not app.results.is_marked(objects[3]))
        self.assert_(app.results.is_marked(objects[4]))
    
    def test_refreshDetailsWithSelected(self):
        def mock_refresh(dupe,group):
            self.called = True
            if self.app.selected_dupes:
                self.assert_(dupe is self.app.selected_dupes[0])
                self.assert_(group is self.app.results.get_group_of_duplicate(dupe))
            else:
                self.assert_(dupe is None)
                self.assert_(group is None)
        
        self.app.RefreshDetailsTable = mock_refresh
        self.called = False
        self.app.SelectPowerMarkerNodePaths(r2np([0,2]))
        self.app.RefreshDetailsWithSelected()
        self.assert_(self.called)
        self.called = False
        self.app.SelectPowerMarkerNodePaths([])
        self.app.RefreshDetailsWithSelected()
        self.assert_(self.called)
    
    def test_makeSelectedReference(self):
        app = self.app
        objects = self.objects
        groups = self.groups
        app.SelectPowerMarkerNodePaths(r2np([0,2]))
        app.MakeSelectedReference()
        self.assert_(groups[0].ref is objects[1])
        self.assert_(groups[1].ref is objects[4])
    
    def test_makeSelectedReference_by_selecting_two_dupes_in_the_same_group(self):
        app = self.app
        objects = self.objects
        groups = self.groups
        app.SelectPowerMarkerNodePaths(r2np([0,1,2]))
        #Only 0 and 2 must go ref, not 1 because it is a part of the same group
        app.MakeSelectedReference()
        self.assert_(groups[0].ref is objects[1])
        self.assert_(groups[1].ref is objects[4])
    
    def test_removeSelected(self):
        app = self.app
        app.SelectPowerMarkerNodePaths(r2np([0,2]))
        app.RemoveSelected()
        self.assertEqual(1,len(app.results.dupes))
        app.RemoveSelected()
        self.assertEqual(1,len(app.results.dupes))
        app.SelectPowerMarkerNodePaths(r2np([0,2]))
        app.RemoveSelected()
        self.assertEqual(0,len(app.results.dupes))
    
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
        app.SelectPowerMarkerNodePaths(r2np([2])) #The dupe of the second, 2 sized group
        app.AddSelectedToIgnoreList()
        self.assertEqual(1,len(app.scanner.ignore_list))
        app.SelectPowerMarkerNodePaths(r2np([0])) #first dupe of the 3 dupes group
        app.AddSelectedToIgnoreList()
        #BOTH the ref and the other dupe should have been added
        self.assertEqual(3,len(app.scanner.ignore_list))
    
    def test_purgeIgnoreList(self):
        app = self.app
        p1 = self.filepath('zerofile')
        p2 = self.filepath('zerofill')
        dne = '/does_not_exist'
        app.scanner.ignore_list.Ignore(dne,p1)
        app.scanner.ignore_list.Ignore(p2,dne)
        app.scanner.ignore_list.Ignore(p1,p2)
        app.PurgeIgnoreList()
        self.assertEqual(1,len(app.scanner.ignore_list))
        self.assert_(app.scanner.ignore_list.AreIgnored(p1,p2))
        self.assert_(not app.scanner.ignore_list.AreIgnored(dne,p1))
    
    def test_only_unicode_is_added_to_ignore_list(self):
        def FakeIgnore(first,second):
            if not isinstance(first,unicode):
                self.fail()
            if not isinstance(second,unicode):
                self.fail()
        
        app = self.app
        app.scanner.ignore_list.Ignore = FakeIgnore
        app.SelectPowerMarkerNodePaths(r2np([2])) #The dupe of the second, 2 sized group
        app.AddSelectedToIgnoreList()
    
    def test_GetOutlineViewChildCounts_out_of_range(self):
        # Out of range requests don't crash and return an empty value
        app = self.app
        # [0, 2] is out of range
        eq_(app.GetOutlineViewChildCounts(1, [0, 2]), []) # no crash
    
    def test_GetOutlineViewValues_out_of_range(self):
        # Out of range requests don't crash and return an empty value
        app = self.app
        # [0, 2] is out of range
        # Directories
        eq_(app.GetOutlineViewValues(1, [0, 2]), []) # no crash
        # Normal results
        app.GetOutlineViewValues(0, [42, 0]) # no crash
    

class TCDupeGuru_renameSelected(TestCase):
    def setUp(self):
        p = self.tmppath()
        fp = open(unicode(p + 'foo bar 1'),mode='w')
        fp.close()
        fp = open(unicode(p + 'foo bar 2'),mode='w')
        fp.close()
        fp = open(unicode(p + 'foo bar 3'),mode='w')
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
    
    def test_simple(self):
        app = self.app
        g = self.groups[0]
        app.SelectPowerMarkerNodePaths(r2np([0]))
        assert app.RenameSelected('renamed')
        names = io.listdir(self.p)
        assert 'renamed' in names
        assert 'foo bar 2' not in names
        eq_(g.dupes[0].name, 'renamed')
    
    def test_none_selected(self):
        app = self.app
        g = self.groups[0]
        app.SelectPowerMarkerNodePaths([])
        self.mock(logging, 'warning', log_calls(lambda msg: None))
        assert not app.RenameSelected('renamed')
        msg = logging.warning.calls[0]['msg']
        eq_('dupeGuru Warning: list index out of range', msg)
        names = io.listdir(self.p)
        assert 'renamed' not in names
        assert 'foo bar 2' in names
        eq_(g.dupes[0].name, 'foo bar 2')
    
    def test_name_already_exists(self):
        app = self.app
        g = self.groups[0]
        app.SelectPowerMarkerNodePaths(r2np([0]))
        self.mock(logging, 'warning', log_calls(lambda msg: None))
        assert not app.RenameSelected('foo bar 1')
        msg = logging.warning.calls[0]['msg']
        assert msg.startswith('dupeGuru Warning: \'foo bar 1\' already exists in')
        names = io.listdir(self.p)
        assert 'foo bar 1' in names
        assert 'foo bar 2' in names
        eq_(g.dupes[0].name, 'foo bar 2')
    
