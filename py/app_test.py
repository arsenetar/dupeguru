#!/usr/bin/env python
"""
Unit Name: dupeguru.tests.app
Created By: Virgil Dupras
Created On: 2007-06-23
Last modified by:$Author: virgil $
Last modified on:$Date: 2009-05-28 16:02:48 +0200 (Thu, 28 May 2009) $
                 $Revision: 4388 $
Copyright 2007 Hardcoded Software (http://www.hardcoded.net)
"""
import unittest
import os

from hsutil.testcase import TestCase
from hsutil import io
from hsutil.path import Path
from hsutil.decorators import log_calls
import hsfs as fs
import hsfs.phys
import hsutil.files
from hsutil.job import nulljob

from . import data, app
from .app import DupeGuru as DupeGuruBase

class DupeGuru(DupeGuruBase):
    def __init__(self):
        DupeGuruBase.__init__(self, data, '/tmp', appid=4)
    
    def _start_job(self, jobid, func):
        func(nulljob)
    

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
    
    def test_CopyOrMove(self):
        # The goal here is just to have a test for a previous blowup I had. I know my test coverage
        # for this unit is pathetic. What's done is done. My approach now is to add tests for
        # every change I want to make. The blowup was caused by a missing import.
        dupe_parent = fs.Directory(None, 'foo')
        dupe = fs.File(dupe_parent, 'bar')
        dupe.copy = log_calls(lambda dest, newname: None)
        self.mock(hsutil.files, 'copy', log_calls(lambda source_path, dest_path: None))
        self.mock(os, 'makedirs', lambda path: None) # We don't want the test to create that fake directory
        self.mock(fs.phys, 'Directory', fs.Directory) # We don't want an error because makedirs didn't work
        app = DupeGuru()
        app.CopyOrMove(dupe, True, 'some_destination', 0)
        self.assertEqual(1, len(hsutil.files.copy.calls))
        call = hsutil.files.copy.calls[0]
        self.assertEqual('some_destination', call['dest_path'])
        self.assertEqual(dupe.path, call['source_path'])
    
    def test_CopyOrMove_clean_empty_dirs(self):
        tmppath = Path(self.tmpdir())
        sourcepath = tmppath + 'source'
        io.mkdir(sourcepath)
        io.open(sourcepath + 'myfile', 'w')
        tmpdir = hsfs.phys.Directory(None, unicode(tmppath))
        myfile = tmpdir['source']['myfile']
        app = DupeGuru()
        self.mock(app, 'clean_empty_dirs', log_calls(lambda path: None))
        app.CopyOrMove(myfile, False, tmppath + 'dest', 0)
        calls = app.clean_empty_dirs.calls
        self.assertEqual(1, len(calls))
        self.assertEqual(sourcepath, calls[0]['path'])
    
    def test_Scan_with_objects_evaluating_to_false(self):
        # At some point, any() was used in a wrong way that made Scan() wrongly return 1
        app = DupeGuru()
        f1, f2 = [fs.File(None, 'foo') for i in range(2)]
        f1.is_ref, f2.is_ref = (False, False)
        assert not (bool(f1) and bool(f2))
        app.directories.get_files = lambda: [f1, f2]
        app.directories._dirs.append('this is just so Scan() doesnt return 3')
        app.start_scanning() # no exception
    

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
    

if __name__ == '__main__':
    unittest.main()