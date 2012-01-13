from objp.util import dontwrap
from cocoa.inter2 import PyTable2, TableView

class ResultTableView(TableView):
    def invalidateMarkings(self): pass

class PyResultTable(PyTable2):
    def powerMarkerMode(self) -> bool:
        return self.model.power_marker
    
    def setPowerMarkerMode_(self, value: bool):
        self.model.power_marker = value
    
    def deltaValuesMode(self) -> bool:
        return self.model.delta_values
    
    def setDeltaValuesMode_(self, value: bool):
        self.model.delta_values = value
    
    def deltaColumns(self) -> list:
        return list(self.model.DELTA_COLUMNS)
    
    def valueForRow_column_(self, row_index: int, column: str) -> object:
        return self.model.get_row_value(row_index, column)
    
    def renameSelected_(self, newname: str) -> bool:
        return self.model.rename_selected(newname)
    
    def sortBy_ascending_(self, key: str, asc: bool):
        self.model.sort(key, asc)
    
    def markSelected(self):
        self.model.app.toggle_selected_mark_state()
    
    def removeSelected(self):
        self.model.app.remove_selected()
    
    def selectedDupeCount(self) -> int:
        return self.model.selected_dupe_count
    
    def pathAtIndex_(self, index: int) -> str:
        row = self.model[index]
        return str(row._dupe.path)
    
    # python --> cocoa
    @dontwrap
    def invalidate_markings(self):
        self.callback.invalidateMarkings()
    