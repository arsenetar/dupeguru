from cocoa.inter2 import PyGUIObject

class PyStatsLabel(PyGUIObject):
    
    def display(self) -> str:
        return self.model.display
