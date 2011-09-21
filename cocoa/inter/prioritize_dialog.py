from hscommon.cocoa.inter import PyGUIObject, PySelectableList

from core.gui.prioritize_dialog import PrioritizeDialog
from .prioritize_list import PyPrioritizeList

class PyPrioritizeDialog(PyGUIObject):
    py_class = PrioritizeDialog
    
    def categoryList(self):
        if not hasattr(self, '_categoryList'):
            self._categoryList = PySelectableList.alloc().initWithPy_(self.py.category_list)
        return self._categoryList
    
    def criteriaList(self):
        if not hasattr(self, '_criteriaList'):
            self._criteriaList = PySelectableList.alloc().initWithPy_(self.py.criteria_list)
        return self._criteriaList
    
    def prioritizationList(self):
        if not hasattr(self, '_prioritizationList'):
            self._prioritizationList = PyPrioritizeList.alloc().initWithPy_(self.py.prioritization_list)
        return self._prioritizationList
    
    def addSelected(self):
        self.py.add_selected()
    
    def removeSelected(self):
        self.py.remove_selected()
    
    def performReprioritization(self):
        self.py.perform_reprioritization()