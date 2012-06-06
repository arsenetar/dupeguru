from objp.util import pyref, dontwrap
from cocoa.inter import PyGUIObject, GUIObjectView

class IgnoreListDialogView(GUIObjectView):
    def show(self): pass

class PyIgnoreListDialog(PyGUIObject):
    def ignoreListTable(self) -> pyref:
        return self.model.ignore_list_table
    
    def removeSelected(self):
        self.model.remove_selected()
    
    def clear(self):
        self.model.clear()
    
    #--- model --> view
    @dontwrap
    def show(self):
        self.callback.show()
    
