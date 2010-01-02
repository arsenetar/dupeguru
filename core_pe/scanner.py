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

class ScannerPE(Scanner):
    cached_blocks = None
    match_scaled = False
    threshold = 75
    
    def _getmatches(self, files, j):
        return matchbase.getmatches(files, self.cached_blocks, self.threshold, self.match_scaled, j)
    
