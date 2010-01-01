# Created By: Virgil Dupras
# Created On: 2006/03/03
# $Id$
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from core.scanner import Scanner as ScannerBase

class ScannerME(ScannerBase):
    @staticmethod
    def _key_func(dupe):
        return (not dupe.is_ref, -dupe.bitrate, -dupe.size)
    
