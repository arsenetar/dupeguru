from cocoa.inter import PyGUIObject

from core.gui.problem_dialog import ProblemDialog

class PyProblemDialog(PyGUIObject):
    py_class = ProblemDialog
    
    def revealSelected(self):
        self.py.reveal_selected_dupe()
    