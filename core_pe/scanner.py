# Created By: Virgil Dupras
# Created On: 2009-10-18
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from core.scanner import Scanner, ScanType

from . import matchblock, matchexif
from .cache import Cache

class ScannerPE(Scanner):
    cache_path = None
    match_scaled = False
    threshold = 75
    
    def _getmatches(self, files, j):
        if self.scan_type == ScanType.FuzzyBlock:
            return matchblock.getmatches(files, self.cache_path, self.threshold, self.match_scaled, j)
        elif self.scan_type == ScanType.ExifTimestamp:
            return matchexif.getmatches(files, self.match_scaled, j)
        else:
            raise Exception("Invalid scan type")
    
    def clear_picture_cache(self):
        cache = Cache(self.cache_path)
        cache.clear()
        cache.close()
    
