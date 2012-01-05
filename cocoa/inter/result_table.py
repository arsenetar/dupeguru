from cocoa.inter import signature, PyTable

class PyResultTable(PyTable):
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
    
    def deltaColumns(self):
        return list(self.py.DELTA_COLUMNS)
    
    @signature('@@:i@')
    def valueForRow_column_(self, row_index, column):
        return self.py.get_row_value(row_index, column)
    
    @signature('c@:@')
    def renameSelected_(self, newname):
        return self.py.rename_selected(newname)
    
    @signature('v@:@c')
    def sortBy_ascending_(self, key, asc):
        self.py.sort(key, asc)
    
    def markSelected(self):
        self.py.app.toggle_selected_mark_state()
    
    def removeSelected(self):
        self.py.app.remove_selected()
    
    @signature('i@:')
    def selectedDupeCount(self):
        return self.py.selected_dupe_count
    
    @signature('@@:i')
    def pathAtIndex_(self, index):
        row = self.py[index]
        return str(row._dupe.path)
    
    # python --> cocoa
    def invalidate_markings(self):
        self.cocoa.invalidateMarkings()
    