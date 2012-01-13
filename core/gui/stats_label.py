# Created By: Virgil Dupras
# Created On: 2010-02-11
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from .base import GUIObject

class StatsLabel(GUIObject):
    def connect(self):
        GUIObject.connect(self)
        self.view.refresh()
    
    @property
    def display(self):
        return self.app.stat_line
    
    def results_changed(self):
        self.view.refresh()
    marking_changed = results_changed
