# Created By: Virgil Dupras
# Created On: 2006/03/03
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import logging


from hsutil import job, io
from hsutil.misc import dedupe
from hsutil.str import get_file_ext, rem_file_ext

from . import engine
from .ignore import IgnoreList

(SCAN_TYPE_FILENAME,
SCAN_TYPE_FIELDS,
SCAN_TYPE_FIELDS_NO_ORDER,
SCAN_TYPE_TAG,
UNUSED, # Must not be removed. Constants here are what scan_type in the prefs are.
SCAN_TYPE_CONTENT,
SCAN_TYPE_CONTENT_AUDIO) = range(7)

SCANNABLE_TAGS = ['track', 'artist', 'album', 'title', 'genre', 'year']

class Scanner(object):
    def __init__(self):
        self.ignore_list = IgnoreList()
        self.discarded_file_count = 0
    
    def _getmatches(self, files, j):
        if self.size_threshold:
            j = j.start_subjob([2, 8])
            for f in j.iter_with_progress(files, 'Read size of %d/%d files'):
                f.size # pre-read, makes a smoother progress if read here (especially for bundles)
            files = [f for f in files if f.size >= self.size_threshold]
        if self.scan_type in (SCAN_TYPE_CONTENT, SCAN_TYPE_CONTENT_AUDIO):
            sizeattr = 'size' if self.scan_type == SCAN_TYPE_CONTENT else 'audiosize'
            return engine.getmatches_by_contents(files, sizeattr, partial=self.scan_type==SCAN_TYPE_CONTENT_AUDIO, j=j)
        else:
            j = j.start_subjob([2, 8])
            kw = {}
            kw['match_similar_words'] = self.match_similar_words
            kw['weight_words'] = self.word_weighting
            kw['min_match_percentage'] = self.min_match_percentage
            if self.scan_type == SCAN_TYPE_FIELDS_NO_ORDER:
                self.scan_type = SCAN_TYPE_FIELDS
                kw['no_field_order'] = True
            func = {
                SCAN_TYPE_FILENAME: lambda f: engine.getwords(rem_file_ext(f.name)),
                SCAN_TYPE_FIELDS: lambda f: engine.getfields(rem_file_ext(f.name)),
                SCAN_TYPE_TAG: lambda f: [engine.getwords(unicode(getattr(f, attrname))) for attrname in SCANNABLE_TAGS if attrname in self.scanned_tags],
            }[self.scan_type]
            for f in j.iter_with_progress(files, 'Read metadata of %d/%d files'):
                f.words = func(f)
            return engine.getmatches(files, j=j, **kw)
    
    @staticmethod
    def _key_func(dupe):
        return (not dupe.is_ref, -dupe.size)
    
    @staticmethod
    def _tie_breaker(ref, dupe):
        refname = rem_file_ext(ref.name).lower()
        dupename = rem_file_ext(dupe.name).lower()
        if 'copy' in refname and 'copy' not in dupename:
            return True
        if refname.startswith(dupename) and (refname[len(dupename):].strip().isdigit()):
            return True
        return len(dupe.path) > len(ref.path)
    
    def GetDupeGroups(self, files, j=job.nulljob):
        j = j.start_subjob([8, 2])
        for f in [f for f in files if not hasattr(f, 'is_ref')]:
            f.is_ref = False
        logging.info('Getting matches')
        matches = self._getmatches(files, j)
        logging.info('Found %d matches' % len(matches))
        j.set_progress(100, 'Removing false matches')
        if not self.mix_file_kind:
            matches = [m for m in matches if get_file_ext(m.first.name) == get_file_ext(m.second.name)]
        matches = [m for m in matches if io.exists(m.first.path) and io.exists(m.second.path)]
        if self.ignore_list:
            j = j.start_subjob(2)
            iter_matches = j.iter_with_progress(matches, 'Processed %d/%d matches against the ignore list')
            matches = [m for m in iter_matches 
                if not self.ignore_list.AreIgnored(unicode(m.first.path), unicode(m.second.path))]
        logging.info('Grouping matches')
        groups = engine.get_groups(matches, j)
        matched_files = dedupe([m.first for m in matches] + [m.second for m in matches])
        self.discarded_file_count = len(matched_files) - sum(len(g) for g in groups)
        groups = [g for g in groups if any(not f.is_ref for f in g)]
        logging.info('Created %d groups' % len(groups))
        j.set_progress(100, 'Doing group prioritization')
        for g in groups:
            g.prioritize(self._key_func, self._tie_breaker)
        return groups
    
    match_similar_words  = False
    min_match_percentage = 80
    mix_file_kind        = True
    scan_type            = SCAN_TYPE_FILENAME
    scanned_tags         = set(['artist', 'title'])
    size_threshold       = 0
    word_weighting       = False
