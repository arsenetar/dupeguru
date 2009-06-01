#!/usr/bin/env python
"""
Unit Name: ignore
Created By: Virgil Dupras
Created On: 2006/05/02
Last modified by:$Author: virgil $
Last modified on:$Date: 2009-05-28 15:22:39 +0200 (Thu, 28 May 2009) $
                 $Revision: 4385 $
Copyright 2004-2006 Hardcoded Software (http://www.hardcoded.net)
"""
import unittest
import cStringIO
import xml.dom.minidom

from .ignore import *

class TCIgnoreList(unittest.TestCase):
    def test_empty(self):
        il = IgnoreList()
        self.assertEqual(0,len(il))
        self.assert_(not il.AreIgnored('foo','bar'))
    
    def test_simple(self):
        il = IgnoreList()
        il.Ignore('foo','bar')
        self.assert_(il.AreIgnored('foo','bar'))
        self.assert_(il.AreIgnored('bar','foo'))
        self.assert_(not il.AreIgnored('foo','bleh'))
        self.assert_(not il.AreIgnored('bleh','bar'))
        self.assertEqual(1,len(il))
    
    def test_multiple(self):
        il = IgnoreList()
        il.Ignore('foo','bar')
        il.Ignore('foo','bleh')
        il.Ignore('bleh','bar')
        il.Ignore('aybabtu','bleh')
        self.assert_(il.AreIgnored('foo','bar'))
        self.assert_(il.AreIgnored('bar','foo'))
        self.assert_(il.AreIgnored('foo','bleh'))
        self.assert_(il.AreIgnored('bleh','bar'))
        self.assert_(not il.AreIgnored('aybabtu','bar'))
        self.assertEqual(4,len(il))
    
    def test_clear(self):
        il = IgnoreList()
        il.Ignore('foo','bar')
        il.Clear()
        self.assert_(not il.AreIgnored('foo','bar'))
        self.assert_(not il.AreIgnored('bar','foo'))
        self.assertEqual(0,len(il))
    
    def test_add_same_twice(self):
        il = IgnoreList()
        il.Ignore('foo','bar')
        il.Ignore('bar','foo')
        self.assertEqual(1,len(il))
    
    def test_save_to_xml(self):
        il = IgnoreList()
        il.Ignore('foo','bar')
        il.Ignore('foo','bleh')
        il.Ignore('bleh','bar')
        f = cStringIO.StringIO()
        il.save_to_xml(f)
        f.seek(0)
        doc = xml.dom.minidom.parse(f)
        root = doc.documentElement
        self.assertEqual('ignore_list',root.nodeName)
        children = [c for c in root.childNodes if c.localName]
        self.assertEqual(2,len(children))
        self.assertEqual(2,len([c for c in children if c.nodeName == 'file']))
        f1,f2 = children
        subchildren = [c for c in f1.childNodes if c.localName == 'file'] +\
            [c for c in f2.childNodes if c.localName == 'file']
        self.assertEqual(3,len(subchildren))
    
    def test_SaveThenLoad(self):
        il = IgnoreList()
        il.Ignore('foo','bar')
        il.Ignore('foo','bleh')
        il.Ignore('bleh','bar')
        il.Ignore(u'\u00e9','bar')
        f = cStringIO.StringIO()
        il.save_to_xml(f)
        f.seek(0)
        il = IgnoreList()
        il.load_from_xml(f)
        self.assertEqual(4,len(il))
        self.assert_(il.AreIgnored(u'\u00e9','bar'))
        
    def test_LoadXML_with_empty_file_tags(self):
        f = cStringIO.StringIO()
        f.write('<?xml version="1.0" encoding="utf-8"?><ignore_list><file><file/></file></ignore_list>')
        f.seek(0)
        il = IgnoreList()
        il.load_from_xml(f)
        self.assertEqual(0,len(il))
        
    def test_AreIgnore_works_when_a_child_is_a_key_somewhere_else(self):
        il = IgnoreList()
        il.Ignore('foo','bar')
        il.Ignore('bar','baz')
        self.assert_(il.AreIgnored('bar','foo'))
    
    
    def test_no_dupes_when_a_child_is_a_key_somewhere_else(self):
        il = IgnoreList()
        il.Ignore('foo','bar')
        il.Ignore('bar','baz')
        il.Ignore('bar','foo')
        self.assertEqual(2,len(il))
    
    def test_iterate(self):
        #It must be possible to iterate through ignore list
        il = IgnoreList()
        expected = [('foo','bar'),('bar','baz'),('foo','baz')]
        for i in expected:
            il.Ignore(i[0],i[1])
        for i in il:
            expected.remove(i) #No exception should be raised
        self.assert_(not expected) #expected should be empty
    
    def test_filter(self):
        il = IgnoreList()
        il.Ignore('foo','bar')
        il.Ignore('bar','baz')
        il.Ignore('foo','baz')
        il.Filter(lambda f,s: f == 'bar')
        self.assertEqual(1,len(il))
        self.assert_(not il.AreIgnored('foo','bar'))
        self.assert_(il.AreIgnored('bar','baz'))
    
    def test_save_with_non_ascii_non_unicode_items(self):
        il = IgnoreList()
        il.Ignore('\xac','\xbf')
        f = cStringIO.StringIO()
        try:
            il.save_to_xml(f)
        except Exception,e:
            self.fail(str(e))
    
    def test_len(self):
        il = IgnoreList()
        self.assertEqual(0,len(il))
        il.Ignore('foo','bar')
        self.assertEqual(1,len(il))
    
    def test_nonzero(self):
        il = IgnoreList()
        self.assert_(not il)
        il.Ignore('foo','bar')
        self.assert_(il)
    

if __name__ == "__main__":
    unittest.main()

