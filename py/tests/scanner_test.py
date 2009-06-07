# Unit Name: dupeguru.tests.scanner_test
# Created By: Virgil Dupras
# Created On: 2006/03/03
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

from hsutil import job
from hsutil.path import Path
from hsutil.testcase import TestCase

from ..engine import getwords, Match
from ..ignore import IgnoreList
from ..scanner import *

class NamedObject(object):
    def __init__(self, name="foobar", size=1):
        self.name = name
        self.size = size
        self.path = Path('')
        self.words = getwords(name)
    

no = NamedObject

class TCScanner(TestCase):
    def test_empty(self):
        s = Scanner()
        r = s.GetDupeGroups([])
        self.assertEqual([],r)
    
    def test_default_settings(self):
        s = Scanner()
        self.assertEqual(80,s.min_match_percentage)
        self.assertEqual(SCAN_TYPE_FILENAME,s.scan_type)
        self.assertEqual(True,s.mix_file_kind)
        self.assertEqual(False,s.word_weighting)
        self.assertEqual(False,s.match_similar_words)
        self.assert_(isinstance(s.ignore_list,IgnoreList))
    
    def test_simple_with_default_settings(self):
        s = Scanner()
        f = [no('foo bar'),no('foo bar'),no('foo bleh')]
        r = s.GetDupeGroups(f)
        self.assertEqual(1,len(r))
        g = r[0]
        #'foo bleh' cannot be in the group because the default min match % is 80
        self.assertEqual(2,len(g)) 
        self.assert_(g.ref in f[:2])
        self.assert_(g.dupes[0] in f[:2])
    
    def test_simple_with_lower_min_match(self):
        s = Scanner()
        s.min_match_percentage = 50
        f = [no('foo bar'),no('foo bar'),no('foo bleh')]
        r = s.GetDupeGroups(f)
        self.assertEqual(1,len(r))
        g = r[0]
        self.assertEqual(3,len(g))
    
    def test_trim_all_ref_groups(self):
        s = Scanner()
        f = [no('foo'),no('foo'),no('bar'),no('bar')]
        f[2].is_ref = True
        f[3].is_ref = True
        r = s.GetDupeGroups(f)
        self.assertEqual(1,len(r))
    
    def test_priorize(self):
        s = Scanner()
        f = [no('foo'),no('foo'),no('bar'),no('bar')]
        f[1].size = 2
        f[2].size = 3
        f[3].is_ref = True
        r = s.GetDupeGroups(f)
        g1,g2 = r
        self.assert_(f[1] in (g1.ref,g2.ref))
        self.assert_(f[0] in (g1.dupes[0],g2.dupes[0]))
        self.assert_(f[3] in (g1.ref,g2.ref))
        self.assert_(f[2] in (g1.dupes[0],g2.dupes[0]))
    
    def test_content_scan(self):
        s = Scanner()
        s.scan_type = SCAN_TYPE_CONTENT
        f = [no('foo'), no('bar'), no('bleh')]
        f[0].md5 = 'foobar'
        f[1].md5 = 'foobar'
        f[2].md5 = 'bleh'
        r = s.GetDupeGroups(f)
        self.assertEqual(len(r), 1)
        self.assertEqual(len(r[0]), 2)
        self.assertEqual(s.discarded_file_count, 0) # don't count the different md5 as discarded!
    
    def test_content_scan_compare_sizes_first(self):
        class MyFile(no):
            def get_md5(file):
                self.fail()
            md5 = property(get_md5)
        
        s = Scanner()
        s.scan_type = SCAN_TYPE_CONTENT
        f = [MyFile('foo',1),MyFile('bar',2)]
        self.assertEqual(0,len(s.GetDupeGroups(f)))
    
    def test_min_match_perc_doesnt_matter_for_content_scan(self):
        s = Scanner()
        s.scan_type = SCAN_TYPE_CONTENT
        f = [no('foo'),no('bar'),no('bleh')]
        f[0].md5 = 'foobar'
        f[1].md5 = 'foobar'
        f[2].md5 = 'bleh'
        s.min_match_percentage = 101
        r = s.GetDupeGroups(f)
        self.assertEqual(1,len(r))
        self.assertEqual(2,len(r[0]))
        s.min_match_percentage = 0
        r = s.GetDupeGroups(f)
        self.assertEqual(1,len(r))
        self.assertEqual(2,len(r[0]))
    
    def test_content_scan_puts_md5_in_words_at_the_end(self):
        s = Scanner()
        s.scan_type = SCAN_TYPE_CONTENT
        f = [no('foo'),no('bar')]
        f[0].md5 = '\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
        f[1].md5 = '\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
        r = s.GetDupeGroups(f)
        g = r[0]
        self.assertEqual(['--'],g.ref.words)
        self.assertEqual(['--'],g.dupes[0].words)
    
    def test_extension_is_not_counted_in_filename_scan(self):
        s = Scanner()
        s.min_match_percentage = 100
        f = [no('foo.bar'),no('foo.bleh')]
        r = s.GetDupeGroups(f)
        self.assertEqual(1,len(r))
        self.assertEqual(2,len(r[0]))
    
    def test_job(self):
        def do_progress(progress,desc=''):
            log.append(progress)
            return True
        s = Scanner()
        log = []
        f = [no('foo bar'),no('foo bar'),no('foo bleh')]
        r = s.GetDupeGroups(f, job.Job(1,do_progress))
        self.assertEqual(0,log[0])
        self.assertEqual(100,log[-1])
    
    def test_mix_file_kind(self):
        s = Scanner()
        s.mix_file_kind = False
        f = [no('foo.1'),no('foo.2')]
        r = s.GetDupeGroups(f)
        self.assertEqual(0,len(r))
    
    def test_word_weighting(self):
        s = Scanner()
        s.min_match_percentage = 75
        s.word_weighting = True
        f = [no('foo bar'),no('foo bar bleh')]
        r = s.GetDupeGroups(f)
        self.assertEqual(1,len(r))
        g = r[0]
        m = g.get_match_of(g.dupes[0])
        self.assertEqual(75,m.percentage) # 16 letters, 12 matching
    
    def test_similar_words(self):
        s = Scanner()
        s.match_similar_words = True
        f = [no('The White Stripes'),no('The Whites Stripe'),no('Limp Bizkit'),no('Limp Bizkitt')]
        r = s.GetDupeGroups(f)
        self.assertEqual(2,len(r))
    
    def test_fields(self):
        s = Scanner()
        s.scan_type = SCAN_TYPE_FIELDS
        f = [no('The White Stripes - Little Ghost'),no('The White Stripes - Little Acorn')]
        r = s.GetDupeGroups(f)
        self.assertEqual(0,len(r))
    
    def test_fields_no_order(self):
        s = Scanner()
        s.scan_type = SCAN_TYPE_FIELDS_NO_ORDER
        f = [no('The White Stripes - Little Ghost'),no('Little Ghost - The White Stripes')]
        r = s.GetDupeGroups(f)
        self.assertEqual(1,len(r))
    
    def test_tag_scan(self):
        s = Scanner()
        s.scan_type = SCAN_TYPE_TAG
        o1 = no('foo')
        o2 = no('bar')
        o1.artist = 'The White Stripes'
        o1.title = 'The Air Near My Fingers'
        o2.artist = 'The White Stripes'
        o2.title = 'The Air Near My Fingers'
        r = s.GetDupeGroups([o1,o2])
        self.assertEqual(1,len(r))
    
    def test_tag_with_album_scan(self):
        s = Scanner()
        s.scan_type = SCAN_TYPE_TAG_WITH_ALBUM
        o1 = no('foo')
        o2 = no('bar')
        o3 = no('bleh')
        o1.artist = 'The White Stripes'
        o1.title = 'The Air Near My Fingers'
        o1.album = 'Elephant'
        o2.artist = 'The White Stripes'
        o2.title = 'The Air Near My Fingers'
        o2.album = 'Elephant'
        o3.artist = 'The White Stripes'
        o3.title = 'The Air Near My Fingers'
        o3.album = 'foobar'
        r = s.GetDupeGroups([o1,o2,o3])
        self.assertEqual(1,len(r))
    
    def test_that_dash_in_tags_dont_create_new_fields(self):
        s = Scanner()
        s.scan_type = SCAN_TYPE_TAG_WITH_ALBUM
        s.min_match_percentage = 50
        o1 = no('foo')
        o2 = no('bar')
        o1.artist = 'The White Stripes - a'
        o1.title = 'The Air Near My Fingers - a'
        o1.album = 'Elephant - a'
        o2.artist = 'The White Stripes - b'
        o2.title = 'The Air Near My Fingers - b'
        o2.album = 'Elephant - b'
        r = s.GetDupeGroups([o1,o2])
        self.assertEqual(1,len(r))
    
    def test_tag_scan_with_different_scanned(self):
        s = Scanner()
        s.scan_type = SCAN_TYPE_TAG
        s.scanned_tags = set(['track', 'year'])
        o1 = no('foo')
        o2 = no('bar')
        o1.artist = 'The White Stripes'
        o1.title = 'some title'
        o1.track = 'foo'
        o1.year = 'bar'
        o2.artist = 'The White Stripes'
        o2.title = 'another title'
        o2.track = 'foo'
        o2.year = 'bar'
        r = s.GetDupeGroups([o1, o2])
        self.assertEqual(1, len(r))
    
    def test_tag_scan_only_scans_existing_tags(self):
        s = Scanner()
        s.scan_type = SCAN_TYPE_TAG
        s.scanned_tags = set(['artist', 'foo'])
        o1 = no('foo')
        o2 = no('bar')
        o1.artist = 'The White Stripes'
        o1.foo = 'foo'
        o2.artist = 'The White Stripes'
        o2.foo = 'bar'
        r = s.GetDupeGroups([o1, o2])
        self.assertEqual(1, len(r)) # Because 'foo' is not scanned, they match
    
    def test_tag_scan_converts_to_str(self):
        s = Scanner()
        s.scan_type = SCAN_TYPE_TAG
        s.scanned_tags = set(['track'])
        o1 = no('foo')
        o2 = no('bar')
        o1.track = 42
        o2.track = 42
        try:
            r = s.GetDupeGroups([o1, o2])
        except TypeError:
            self.fail()
        self.assertEqual(1, len(r))
    
    def test_tag_scan_non_ascii(self):
        s = Scanner()
        s.scan_type = SCAN_TYPE_TAG
        s.scanned_tags = set(['title'])
        o1 = no('foo')
        o2 = no('bar')
        o1.title = u'foobar\u00e9'
        o2.title = u'foobar\u00e9'
        try:
            r = s.GetDupeGroups([o1, o2])
        except UnicodeEncodeError:
            self.fail()
        self.assertEqual(1, len(r))
    
    def test_audio_content_scan(self):
        s = Scanner()
        s.scan_type = SCAN_TYPE_CONTENT_AUDIO
        f = [no('foo'),no('bar'),no('bleh')]
        f[0].md5 = 'foo'
        f[1].md5 = 'bar'
        f[2].md5 = 'bleh'
        f[0].md5partial = 'foo'
        f[1].md5partial = 'foo'
        f[2].md5partial = 'bleh'
        f[0].audiosize = 1
        f[1].audiosize = 1
        f[2].audiosize = 1
        r = s.GetDupeGroups(f)
        self.assertEqual(1,len(r))
        self.assertEqual(2,len(r[0]))
        
    def test_audio_content_scan_compare_sizes_first(self):
        class MyFile(no):
            def get_md5(file):
                self.fail()
            md5partial = property(get_md5)
        
        s = Scanner()
        s.scan_type = SCAN_TYPE_CONTENT_AUDIO
        f = [MyFile('foo'),MyFile('bar')]
        f[0].audiosize = 1
        f[1].audiosize = 2
        self.assertEqual(0,len(s.GetDupeGroups(f)))
    
    def test_ignore_list(self):
        s = Scanner()
        f1 = no('foobar')
        f2 = no('foobar')
        f3 = no('foobar')
        f1.path = Path('dir1/foobar')
        f2.path = Path('dir2/foobar')
        f3.path = Path('dir3/foobar')
        s.ignore_list.Ignore(str(f1.path),str(f2.path))
        s.ignore_list.Ignore(str(f1.path),str(f3.path))
        r = s.GetDupeGroups([f1,f2,f3])
        self.assertEqual(1,len(r))
        g = r[0]
        self.assertEqual(1,len(g.dupes))
        self.assert_(f1 not in g)
        self.assert_(f2 in g)
        self.assert_(f3 in g)
        # Ignored matches are not counted as discarded
        self.assertEqual(s.discarded_file_count, 0)
    
    def test_ignore_list_checks_for_unicode(self):
        #scanner was calling path_str for ignore list checks. Since the Path changes, it must
        #be unicode(path)
        s = Scanner()
        f1 = no('foobar')
        f2 = no('foobar')
        f3 = no('foobar')
        f1.path = Path(u'foo1\u00e9')
        f2.path = Path(u'foo2\u00e9')
        f3.path = Path(u'foo3\u00e9')
        s.ignore_list.Ignore(unicode(f1.path),unicode(f2.path))
        s.ignore_list.Ignore(unicode(f1.path),unicode(f3.path))
        r = s.GetDupeGroups([f1,f2,f3])
        self.assertEqual(1,len(r))
        g = r[0]
        self.assertEqual(1,len(g.dupes))
        self.assert_(f1 not in g)
        self.assert_(f2 in g)
        self.assert_(f3 in g)
    
    def test_custom_match_factory(self):
        class MatchFactory(object):
            def getmatches(self,objects,j=None):
                return [Match(objects[0], objects[1], 420)]
            
        
        s = Scanner()
        s.match_factory = MatchFactory()
        o1,o2 = no('foo'),no('bar')
        groups = s.GetDupeGroups([o1,o2])
        self.assertEqual(1,len(groups))
        g = groups[0]
        self.assertEqual(2,len(g))
        g.switch_ref(o1)
        m = g.get_match_of(o2)
        self.assertEqual((o1,o2,420),m)
    
    def test_file_evaluates_to_false(self):
        # A very wrong way to use any() was added at some point, causing resulting group list
        # to be empty.
        class FalseNamedObject(NamedObject):
            def __nonzero__(self):
                return False
            
        
        s = Scanner()
        f1 = FalseNamedObject('foobar')
        f2 = FalseNamedObject('foobar')
        r = s.GetDupeGroups([f1,f2])
        self.assertEqual(1,len(r))
    
    def test_size_threshold(self):
        # Only file equal or higher than the size_threshold in size are scanned
        s = Scanner()
        f1 = no('foo', 1)
        f2 = no('foo', 2)
        f3 = no('foo', 3)
        s.size_threshold = 2
        groups = s.GetDupeGroups([f1,f2,f3])
        self.assertEqual(len(groups), 1)
        [group] = groups
        self.assertEqual(len(group), 2)
        self.assertTrue(f1 not in group)
        self.assertTrue(f2 in group)
        self.assertTrue(f3 in group)
    
    def test_tie_breaker_path_deepness(self):
        # If there is a tie in prioritization, path deepness is used as a tie breaker
        s = Scanner()
        o1, o2 = no('foo'), no('foo')
        o1.path = Path('foo')
        o2.path = Path('foo/bar')
        [group] = s.GetDupeGroups([o1, o2])
        self.assertTrue(group.ref is o2)
    
    def test_tie_breaker_copy(self):
        # if copy is in the words used (even if it has a deeper path), it becomes a dupe
        s = Scanner()
        o1, o2 = no('foo bar Copy'), no('foo bar')
        o1.path = Path('deeper/path')
        o2.path = Path('foo')
        [group] = s.GetDupeGroups([o1, o2])
        self.assertTrue(group.ref is o2)
    
    def test_tie_breaker_same_name_plus_digit(self):
        # if ref has the same words as dupe, but has some just one extra word which is a digit, it
        # becomes a dupe
        s = Scanner()
        o1, o2 = no('foo bar 42'), no('foo bar')
        o1.path = Path('deeper/path')
        o2.path = Path('foo')
        [group] = s.GetDupeGroups([o1, o2])
        self.assertTrue(group.ref is o2)
    
    def test_partial_group_match(self):
        # Count the number od discarded matches (when a file doesn't match all other dupes of the 
        # group) in Scanner.discarded_file_count
        s = Scanner()
        o1, o2, o3 = no('a b'), no('a'), no('b')
        s.min_match_percentage = 50
        [group] = s.GetDupeGroups([o1, o2, o3])
        self.assertEqual(len(group), 2)
        self.assertTrue(o1 in group)
        self.assertTrue(o2 in group)
        self.assertTrue(o3 not in group)
        self.assertEqual(s.discarded_file_count, 1)
    

class TCScannerME(TestCase):
    def test_priorize(self):
        # in ScannerME, bitrate goes first (right after is_ref) in priorization
        s = ScannerME()
        o1, o2 = no('foo'), no('foo')
        o1.bitrate = 1
        o2.bitrate = 2
        [group] = s.GetDupeGroups([o1, o2])
        self.assertTrue(group.ref is o2)
    
