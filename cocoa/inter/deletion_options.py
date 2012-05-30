# Created On: 2012-05-30
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from cocoa.inter import PyGUIObject, GUIObjectView

class DeletionOptionsView(GUIObjectView):
    def updateMsg_(self, msg: str): pass
    def show(self) -> bool: pass

class PyDeletionOptions(PyGUIObject):
    def setHardlink_(self, hardlink: bool):
        self.model.hardlink = hardlink
    
    def setDirect_(self, direct: bool):
        self.model.direct = direct
    
    #--- model --> view
    def update_msg(self, msg):
        self.callback.updateMsg_(msg)
    
    def show(self):
        return self.callback.show()
    
