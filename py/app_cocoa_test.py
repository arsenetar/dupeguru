#!/usr/bin/env python
"""
Unit Name: dupeguru.tests.app_cocoa
Created By: Virgil Dupras
Created On: 2006/11/11
Last modified by:$Author: virgil $
Last modified on:$Date: 2009-05-29 17:51:41 +0200 (Fri, 29 May 2009) $
                 $Revision: 4409 $
Copyright 2006 Hardcoded Software (http://www.hardcoded.net)
"""
import tempfile
import shutil
import logging

from hsutil.path import Path
from hsutil.testcase import TestCase
from hsutil.decorators import log_calls
import hsfs.phys
import os.path as op

from . import engine, data
try:
    from .app_cocoa import DupeGuru as DupeGuruBase, DGDirectory
except ImportError:
    from nose.plugins.skip import SkipTest
    raise SkipTest("These tests can only be run on OS X")
from .results_test import GetTestGroups

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
        app = self.app
        self.assertEqual(0,app.add_directory(self.datadirpath()))
        self.assertEqual(1,len(app.directories))
    
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
    
    def test_dirclass(self):
        self.assert_(self.app.directories.dirclass is DGDirectory)
    

class TCDupeGuru_renameSelected(TestCase):
    def setUp(self):
        p = Path(tempfile.mkdtemp())
        fp = open(str(p + 'foo bar 1'),mode='w')
        fp.close()
        fp = open(str(p + 'foo bar 2'),mode='w')
        fp.close()
        fp = open(str(p + 'foo bar 3'),mode='w')
        fp.close()
        refdir = hsfs.phys.Directory(None,str(p))
        matches = engine.MatchFactory().getmatches(refdir.files)
        groups = engine.get_groups(matches)
        g = groups[0]
        g.prioritize(lambda x:x.name)
        app = DupeGuru()
        app.results.groups = groups
        self.app = app
        self.groups = groups
        self.p = p
        self.refdir = refdir
    
    def tearDown(self):
        shutil.rmtree(str(self.p))
    
    def test_simple(self):
        app = self.app
        refdir = self.refdir
        g = self.groups[0]
        app.SelectPowerMarkerNodePaths(r2np([0]))
        self.assert_(app.RenameSelected('renamed'))
        self.assert_('renamed' in refdir)
        self.assert_('foo bar 2' not in refdir)
        self.assert_(g.dupes[0] is refdir['renamed'])
        self.assert_(g.dupes[0] in refdir)
    
    def test_none_selected(self):
        app = self.app
        refdir = self.refdir
        g = self.groups[0]
        app.SelectPowerMarkerNodePaths([])
        self.mock(logging, 'warning', log_calls(lambda msg: None))
        self.assert_(not app.RenameSelected('renamed'))
        msg = logging.warning.calls[0]['msg']
        self.assertEqual('dupeGuru Warning: list index out of range', msg)
        self.assert_('renamed' not in refdir)
        self.assert_('foo bar 2' in refdir)
        self.assert_(g.dupes[0] is refdir['foo bar 2'])
    
    def test_name_already_exists(self):
        app = self.app
        refdir = self.refdir
        g = self.groups[0]
        app.SelectPowerMarkerNodePaths(r2np([0]))
        self.mock(logging, 'warning', log_calls(lambda msg: None))
        self.assert_(not app.RenameSelected('foo bar 1'))
        msg = logging.warning.calls[0]['msg']
        self.assert_(msg.startswith('dupeGuru Warning: \'foo bar 2\' already exists in'))
        self.assert_('foo bar 1' in refdir)
        self.assert_('foo bar 2' in refdir)
        self.assert_(g.dupes[0] is refdir['foo bar 2'])
    
