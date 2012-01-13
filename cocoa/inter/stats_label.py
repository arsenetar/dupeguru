from cocoa.inter2 import PyGUIObject2, GUIObjectView

class StatsLabelView(GUIObjectView):
    pass

class PyStatsLabel(PyGUIObject2):
    
    def display(self) -> str:
        return self.model.display
