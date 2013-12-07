import logging
from objp.util import pyref, dontwrap
from . import proxy

class GUIObjectView:
    def refresh(self): pass

class PyGUIObject:
    def __init__(self, model: pyref):
        self.model = model
        self.callback = None
    
    # This *has* to be called right after initialization.
    def bindCallback_(self, callback: pyref):
        self.callback = callback
        self.model.view = self
    
    # Call this before the ObjC callback is deallocated to avoid calls to that deallocated instance.
    def free(self):
        self.model.view = None
        self.callback = None
    
    def modelRef(self) -> pyref:
        return self.model
    
    #--- Python -> Cocoa
    @dontwrap
    def refresh(self):
        self.callback.refresh()

class PyTextField(PyGUIObject):
    def text(self) -> str:
        return self.model.text
    
    def setText_(self, newtext: str):
        self.model.text = newtext
    

class SelectableListView(GUIObjectView):
    def updateSelection(self): pass

class PySelectableList(PyGUIObject):
    def items(self) -> list:
        # Should normally always return strings
        return self.model[:]
    
    def selectIndex_(self, index: int):
        self.model.select(index)
    
    def selectedIndex(self) -> int:
        result = self.model.selected_index
        if result is None:
            result = -1
        return result
    
    def selectedIndexes(self) -> list:
        return self.model.selected_indexes
    
    def selectIndexes_(self, indexes: list):
        self.model.select(indexes)
    
    def searchByPrefix_(self, prefix: str) -> int:
        return self.model.search_by_prefix(prefix)
    
    #--- model --> view
    @dontwrap
    def update_selection(self):
        self.callback.updateSelection()

class ColumnsView:
    def restoreColumns(self): pass
    def setColumn_visible_(self, colname: str, visible: bool): pass

class PyColumns(PyGUIObject):
    def columnNamesInOrder(self) -> list:
        return self.model.colnames
    
    def columnDisplay_(self, colname: str) -> str:
        return self.model.column_display(colname)
    
    def columnIsVisible_(self, colname: str) -> bool:
        return self.model.column_is_visible(colname)
    
    def columnWidth_(self, colname: str) -> int:
        return self.model.column_width(colname)
    
    def moveColumn_toIndex_(self, colname: str, index: int):
        self.model.move_column(colname, index)
    
    def resizeColumn_toWidth_(self, colname: str, newwidth: int):
        self.model.resize_column(colname, newwidth)
    
    def setColumn_defaultWidth_(self, colname: str, width: int):
        self.model.set_default_width(colname, width)
    
    def menuItems(self) -> list:
        return self.model.menu_items()
    
    def toggleMenuItem_(self, index: int) -> bool:
        return self.model.toggle_menu_item(index)
    
    def resetToDefaults(self):
        self.model.reset_to_defaults()
    
    #--- Python --> Cocoa
    @dontwrap
    def restore_columns(self):
        self.callback.restoreColumns()
    
    @dontwrap
    def set_column_visible(self, colname: str, visible):
        self.callback.setColumn_visible_(colname, visible)

class OutlineView(GUIObjectView):
    def startEditing(self): pass
    def stopEditing(self): pass
    def updateSelection(self): pass

class PyOutline(PyGUIObject):
    def cancelEdits(self):
        self.model.cancel_edits()
    
    def canEditProperty_atPath_(self, property: str, path: list) -> bool:
        node = self.model.get_node(path)
        assert node is self.model.selected_node
        return getattr(node, 'can_edit_' + property, False)
    
    def saveEdits(self):
        self.model.save_edits()
    
    def selectedPath(self) -> list:
        return self.model.selected_path
    
    def setSelectedPath_(self, path: list):
        self.model.selected_path = path
    
    def selectedPaths(self) -> list:
        return self.model.selected_paths
    
    def setSelectedPaths_(self, paths: list):
        self.model.selected_paths = paths
    
    def property_valueAtPath_(self, property: str, path: list) -> object:
        try:
            return getattr(self.model.get_node(path), property)
        except IndexError:
            logging.warning("%r doesn't have a node at path %r", self.model, path)
            return ''
    
    def setProperty_value_atPath_(self, property: str, value: object, path: list):
        setattr(self.model.get_node(path), property, value)
    
    #--- Python -> Cocoa
    @dontwrap
    def start_editing(self):
        self.callback.startEditing()
    
    @dontwrap
    def stop_editing(self):
        self.callback.stopEditing()
    
    @dontwrap
    def update_selection(self):
        self.callback.updateSelection()

class TableView(GUIObjectView):
    def showSelectedRow(self): pass
    def startEditing(self): pass
    def stopEditing(self): pass
    def updateSelection(self): pass

class PyTable(PyGUIObject):
    #--- Helpers
    @dontwrap
    def _getrow(self, row):
        try:
            return self.model[row]
        except IndexError:
            msg = "Trying to get an out of bounds row ({} / {}) on table {}"
            logging.warning(msg.format(row, len(self.model), self.model.__class__.__name__))
    
    #--- Cocoa --> Python
    def columns(self) -> pyref:
        return self.model.columns
    
    def add(self):
        self.model.add()
    
    def cancelEdits(self):
        self.model.cancel_edits()
    
    def canEditColumn_atRow_(self, column: str, row: int) -> object:
        return self.model.can_edit_cell(column, row)
    
    def deleteSelectedRows(self):
        self.model.delete()
    
    def numberOfRows(self) -> int:
        return len(self.model)
    
    def saveEdits(self):
        self.model.save_edits()
    
    def selectRows_(self, rows: list):
        self.model.select(list(rows))
    
    def selectedRows(self) -> list:
        return self.model.selected_indexes
    
    def selectionAsCSV(self) -> str:
        return self.model.selection_as_csv()
    
    def setValue_forColumn_row_(self, value: object, column: str, row: int):
        # this try except is important for the case while a row is in edition mode and the delete
        # button is clicked.
        try:
            self._getrow(row).set_cell_value(column, value)
        except AttributeError:
            msg = "Trying to set an attribute that can't: {} with value {} at row {} on table {}"
            logging.warning(msg.format(column, value, row, self.model.__class__.__name__))
            raise
    
    def sortByColumn_desc_(self, column: str, desc: bool):
        self.model.sort_by(column, desc=desc)
    
    def valueForColumn_row_(self, column: str, row: int) -> object:
        return self._getrow(row).get_cell_value(column)
    
    #--- Python -> Cocoa
    @dontwrap
    def show_selected_row(self):
        self.callback.showSelectedRow()
    
    @dontwrap
    def start_editing(self):
        self.callback.startEditing()
    
    @dontwrap
    def stop_editing(self):
        self.callback.stopEditing()
    
    @dontwrap
    def update_selection(self):
        self.callback.updateSelection()

class ProgressWindowView(GUIObjectView):
    def setProgress_(self, progress: int): pass
    def showWindow(self): pass
    def closeWindow(self): pass

class PyProgressWindow(PyGUIObject):
    def jobdescTextField(self) -> pyref:
        return self.model.jobdesc_textfield
    
    def progressdescTextField(self) -> pyref:
        return self.model.progressdesc_textfield
    
    def pulse(self):
        self.model.pulse()
    
    def cancel(self):
        self.model.cancel()
    
    #--- Python -> Cocoa
    @dontwrap
    def set_progress(self, last_progress):
        self.callback.setProgress_(last_progress)
        
    @dontwrap
    def show(self):
        self.callback.showWindow()
    
    @dontwrap
    def close(self):
        self.callback.closeWindow()
    

class BaseAppView:
    def showMessage_(self, msg: str): pass
    
class PyBaseApp(PyGUIObject):
    def appName(self) -> str:
        return self.model.PROMPT_NAME
    
    def appLongName(self) -> str:
        return self.model.NAME
    
    #--- Python --> Cocoa
    @dontwrap
    def get_default(self, key_name):
        return proxy.prefValue_(key_name)
    
    @dontwrap
    def set_default(self, key_name, value):
        proxy.setPrefValue_value_(key_name, value)
    
    @dontwrap
    def show_message(self, msg):
        self.callback.showMessage_(msg)

