# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-10-23
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import hashlib

from nose.tools import eq_

from hsutil.testcase import TestCase
from core.fs import File
from core.tests.directories_test import create_fake_fs

from .. import fs

class TCBundle(TestCase):
    def test_size_aggregates_subfiles(self):
        p = create_fake_fs(self.tmppath())
        b = fs.Bundle(p)
        eq_(b.size, 12)
    
    def test_md5_aggregate_subfiles_sorted(self):
        #dir.allfiles can return child in any order. Thus, bundle.md5 must aggregate
        #all files' md5 it contains, but it must make sure that it does so in the 
        #same order everytime.
        p = create_fake_fs(self.tmppath())
        b = fs.Bundle(p)
        md5s = File(p + ('dir1', 'file1.test')).md5
        md5s += File(p + ('dir2', 'file2.test')).md5
        md5s += File(p + ('dir3', 'file3.test')).md5
        md5s += File(p + 'file1.test').md5
        md5s += File(p + 'file2.test').md5
        md5s += File(p + 'file3.test').md5
        md5 = hashlib.md5(md5s)
        eq_(b.md5, md5.digest())
    
    def test_has_file_attrs(self):
        #a Bundle must behave like a file, so it must have ctime and mtime attributes
        b = fs.Bundle(self.tmppath())
        assert b.mtime > 0
        assert b.ctime > 0
        eq_(b.extension, '')
    