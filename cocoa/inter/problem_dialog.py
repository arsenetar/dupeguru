from objp.util import pyref
from cocoa.inter import PyGUIObject

class PyProblemDialog(PyGUIObject):
    def problemTable(self) -> pyref:
        return self.model.problem_table
    
    def revealSelected(self):
        self.model.reveal_selected_dupe()
