# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-02-06
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from hsutil.notify import Listener

class GUIObject(Listener):
    def __init__(self, view, app):
        Listener.__init__(self, app)
        self.view = view
        self.app = app
    
    def directories_changed(self):
        pass
    
    def dupes_selected(self):
        pass
    
    def results_changed(self):
        pass
    
