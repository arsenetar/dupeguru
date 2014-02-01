# Created By: Virgil Dupras
# Created On: 2011-09-06
# Copyright 2014 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt5.QtCore import Qt, QAbstractListModel, QItemSelection, QItemSelectionModel

class SelectableList(QAbstractListModel):
    def __init__(self, model, view, **kwargs):
        super().__init__(**kwargs)
        self._updating = False
        self.view = view
        self.model = model
        self.view.setModel(self)
        self.model.view = self
    
    #--- Override
    def data(self, index, role):
        if not index.isValid():
            return None
        # We need EditRole for QComboBoxes with setEditable(True)
        if role in {Qt.DisplayRole, Qt.EditRole}:
            return self.model[index.row()]
        return None
    
    def rowCount(self, index):
        if index.isValid():
            return 0
        return len(self.model)
    
    #--- Virtual
    def _updateSelection(self):
        raise NotImplementedError()
    
    def _restoreSelection(self):
        raise NotImplementedError()
    
    #--- model --> view
    def refresh(self):
        self._updating = True
        self.reset()
        self._updating = False
        self._restoreSelection()
    
    def update_selection(self):
        self._restoreSelection()

class ComboboxModel(SelectableList):
    def __init__(self, model, view, **kwargs):
        super().__init__(model, view, **kwargs)
        self.view.currentIndexChanged[int].connect(self.selectionChanged)
    
    #--- Override
    def _updateSelection(self):
        index = self.view.currentIndex()
        if index != self.model.selected_index:
            self.model.select(index)
    
    def _restoreSelection(self):
        index = self.model.selected_index
        if index is not None:
            self.view.setCurrentIndex(index)
    
    #--- Events
    def selectionChanged(self, index):
        if not self._updating:
            self._updateSelection()

class ListviewModel(SelectableList):
    def __init__(self, model, view, **kwargs):
        super().__init__(model, view, **kwargs)
        self.view.selectionModel().selectionChanged[(QItemSelection, QItemSelection)].connect(
            self.selectionChanged)
    
    #--- Override
    def _updateSelection(self):
        newIndexes = [modelIndex.row() for modelIndex in self.view.selectionModel().selectedRows()]
        if newIndexes != self.model.selected_indexes:
            self.model.select(newIndexes)
    
    def _restoreSelection(self):
        newSelection = QItemSelection()
        for index in self.model.selected_indexes:
            newSelection.select(self.createIndex(index, 0), self.createIndex(index, 0))
        self.view.selectionModel().select(newSelection, QItemSelectionModel.ClearAndSelect)
        if len(newSelection.indexes()):
            currentIndex = newSelection.indexes()[0]
            self.view.selectionModel().setCurrentIndex(currentIndex, QItemSelectionModel.Current)
            self.view.scrollTo(currentIndex)
    #--- Events
    def selectionChanged(self, index):
        if not self._updating:
            self._updateSelection()
    
