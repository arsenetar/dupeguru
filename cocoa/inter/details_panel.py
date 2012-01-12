from cocoa.inter2 import PyGUIObject

class PyDetailsPanel(PyGUIObject):
    def numberOfRows(self) -> int:
        return self.model.row_count()
    
    def valueForColumn_row_(self, column: str, row: int) -> object:
        return self.model.row(row)[int(column)]
