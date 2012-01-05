from cocoa.inter import PyGUIObject

from core.gui.stats_label import StatsLabel

class PyStatsLabel(PyGUIObject):
    py_class = StatsLabel
    
    def display(self):
        return self.py.display
