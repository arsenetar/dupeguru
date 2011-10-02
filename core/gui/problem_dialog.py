# Created By: Virgil Dupras
# Created On: 2010-04-12
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hscommon.notify import Broadcaster

from .base import GUIObject

class ProblemDialog(GUIObject, Broadcaster):
    def __init__(self, view, app):
        GUIObject.__init__(self, view, app)
        Broadcaster.__init__(self)
        self._selected_dupe = None
    
    def reveal_selected_dupe(self):
        if self._selected_dupe is not None:
            self.app.view.reveal_path(self._selected_dupe.path)
    
    def select_dupe(self, dupe):
        self._selected_dupe = dupe
    
    #--- Event Handlers
    def problems_changed(self):
        self._selected_dupe = None
        self.notify('problems_changed')
    
