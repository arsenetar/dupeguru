from objp.util import pyref
from cocoa.inter import PyGUIObject, GUIObjectView

class PrioritizeDialogView(GUIObjectView):
    pass

class PyPrioritizeDialog(PyGUIObject):
    def categoryList(self) -> pyref:
        return self.model.category_list
    
    def criteriaList(self) -> pyref:
        return self.model.criteria_list
    
    def prioritizationList(self) -> pyref:
        return self.model.prioritization_list
    
    def addSelected(self):
        self.model.add_selected()
    
    def removeSelected(self):
        self.model.remove_selected()
    
    def performReprioritization(self):
        self.model.perform_reprioritization()
