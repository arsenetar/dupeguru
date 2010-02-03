# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from hsutil.cocoa import signature

from core.app_cocoa_inter import PyDupeGuruBase
from core_me.app_cocoa import DupeGuruME
from core.scanner import (SCAN_TYPE_FILENAME, SCAN_TYPE_FIELDS, SCAN_TYPE_FIELDS_NO_ORDER,
    SCAN_TYPE_TAG, SCAN_TYPE_CONTENT, SCAN_TYPE_CONTENT_AUDIO)

# Fix py2app imports which chokes on relative imports
from core_me import app_cocoa, data, fs, scanner
from hsmedia import aiff, flac, genres, id3v1, id3v2, mp4, mpeg, ogg, wma

class PyDupeGuru(PyDupeGuruBase):
    def init(self):
        self = super(PyDupeGuru,self).init()
        self.app = DupeGuruME()
        return self
    
    def removeDeadTracks(self):
        self.app.remove_dead_tracks()
    
    def scanDeadTracks(self):
        self.app.scan_dead_tracks()
    
    #---Information
    @signature('i@:')
    def deadTrackCount(self):
        return len(self.app.dead_tracks)
    
    #---Properties
    def setMinMatchPercentage_(self, percentage):
        self.app.scanner.min_match_percentage = int(percentage)
    
    def setScanType_(self, scan_type):
        try:
            self.app.scanner.scan_type = [
                SCAN_TYPE_FILENAME,
                SCAN_TYPE_FIELDS,
                SCAN_TYPE_FIELDS_NO_ORDER,
                SCAN_TYPE_TAG,
                SCAN_TYPE_CONTENT,
                SCAN_TYPE_CONTENT_AUDIO
            ][scan_type]
        except IndexError:
            pass
    
    def setWordWeighting_(self, words_are_weighted):
        self.app.scanner.word_weighting = words_are_weighted
    
    def setMatchSimilarWords_(self, match_similar_words):
        self.app.scanner.match_similar_words = match_similar_words
    
    def enable_scanForTag_(self, enable, scan_tag):
        if enable:
            self.app.scanner.scanned_tags.add(scan_tag)
        else:
            self.app.scanner.scanned_tags.discard(scan_tag)
    
    #---Registration
    def appName(self):
        return "dupeGuru Music Edition"
    
