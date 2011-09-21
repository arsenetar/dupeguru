from hscommon.cocoa.inter import signature, PyTable

from core.gui.result_table import ResultTable

class PyResultTable(PyTable):
    py_class = ResultTable
    
    @signature('c@:')
    def powerMarkerMode(self):
        return self.py.power_marker
    
    @signature('v@:c')
    def setPowerMarkerMode_(self, value):
        self.py.power_marker = value
    
    @signature('c@:')
    def deltaValuesMode(self):
        return self.py.delta_values
    
    @signature('v@:c')
    def setDeltaValuesMode_(self, value):
        self.py.delta_values = value
    
    @signature('@@:ii')
    def valueForRow_column_(self, row_index, column):
        return self.py.get_row_value(row_index, column)
    
    @signature('c@:@')
    def renameSelected_(self, newname):
        return self.py.rename_selected(newname)
    
    @signature('v@:ic')
    def sortBy_ascending_(self, key, asc):
        self.py.sort(key, asc)
    
    def markSelected(self):
        self.py.app.toggle_selected_mark_state()
    
    def removeSelected(self):
        self.py.app.remove_selected()
    
    @signature('i@:')
    def selectedDupeCount(self):
        return self.py.selected_dupe_count
    
    # python --> cocoa
    def invalidate_markings(self):
        self.cocoa.invalidateMarkings()
    