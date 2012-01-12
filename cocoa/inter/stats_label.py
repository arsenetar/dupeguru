from cocoa.inter2 import PyGUIObject, GUIObjectView

class StatsLabelView(GUIObjectView):
    pass

class PyStatsLabel(PyGUIObject):
    
    def display(self) -> str:
        return self.model.display
