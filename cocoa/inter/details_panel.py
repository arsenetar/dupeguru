from hscommon.cocoa.inter import signature, PyGUIObject

from core.gui.details_panel import DetailsPanel

class PyDetailsPanel(PyGUIObject):
    py_class = DetailsPanel
    @signature('i@:')
    def numberOfRows(self):
        return self.py.row_count()
    
    @signature('@@:@i')
    def valueForColumn_row_(self, column, row):
        return self.py.row(row)[int(column)]
