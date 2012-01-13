from objp.util import pyref
from cocoa.inter2 import PyGUIObject2

class PyProblemDialog(PyGUIObject2):
    def problemTable(self) -> pyref:
        return self.model.problem_table
    
    def revealSelected(self):
        self.model.reveal_selected_dupe()
