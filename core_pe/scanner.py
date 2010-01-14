# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-10-18
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from core.scanner import Scanner

from . import matchbase
from .cache import Cache

class ScannerPE(Scanner):
    cache_path = None
    match_scaled = False
    threshold = 75
    
    def _getmatches(self, files, j):
        return matchbase.getmatches(files, self.cache_path, self.threshold, self.match_scaled, j)
    
    def clear_picture_cache(self):
        cache = Cache(self.cache_path)
        cache.clear()
        cache.close()
    
