from cocoa.inter2 import PyGUIObject2, GUIObjectView

class DetailsPanelView(GUIObjectView):
    pass

class PyDetailsPanel(PyGUIObject2):
    def numberOfRows(self) -> int:
        return self.model.row_count()
    
    def valueForColumn_row_(self, column: str, row: int) -> object:
        return self.model.row(row)[int(column)]
