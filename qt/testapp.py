# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-10-04
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from .se.app import DupeGuru

class TestApp(DupeGuru):
    # Use this for as a mock for UI testing.
    def mustShowNag(self):
        pass
    
    def _setup(self):
        self.prefs = self._create_preferences()
        self.prefs.load()
    
