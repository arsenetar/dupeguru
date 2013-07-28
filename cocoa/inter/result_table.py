from objp.util import dontwrap
from cocoa.inter import PyTable, TableView

class ResultTableView(TableView):
    def invalidateMarkings(self): pass

class PyResultTable(PyTable):
    def powerMarkerMode(self) -> bool:
        return self.model.power_marker
    
    def setPowerMarkerMode_(self, value: bool):
        self.model.power_marker = value
    
    def deltaValuesMode(self) -> bool:
        return self.model.delta_values
    
    def setDeltaValuesMode_(self, value: bool):
        self.model.delta_values = value
    
    def valueForRow_column_(self, row_index: int, column: str) -> object:
        return self.model.get_row_value(row_index, column)
    
    def isDeltaAtRow_column_(self, row_index: int, column: str) -> bool:
        row = self.model[row_index]
        return row.is_cell_delta(column)
    
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
    