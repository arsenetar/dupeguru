# Created By: Virgil Dupras
# Created On: 2010-02-06
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hscommon.notify import Listener
from hscommon.gui.base import NoopGUI

class DupeGuruGUIObject(Listener):
    def __init__(self, app):
        Listener.__init__(self, app)
        self.app = app
    
    def directories_changed(self):
        pass
    
    def dupes_selected(self):
        pass
    
    def marking_changed(self):
        pass
    
    def results_changed(self):
        pass
    
    def results_changed_but_keep_selection(self):
        pass
    
