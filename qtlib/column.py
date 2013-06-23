# Created By: Virgil Dupras
# Created On: 2009-11-25
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4.QtCore import Qt

class Column:
    def __init__(self, attrname, defaultWidth, editor=None, alignment=Qt.AlignLeft, cantTruncate=False):
        self.attrname = attrname
        self.defaultWidth = defaultWidth
        self.editor = editor
        self.alignment = alignment
        # This is to indicate, during printing, that a column can't have its data truncated.
        self.cantTruncate = cantTruncate
    

class Columns:
    def __init__(self, model, columns, headerView):
        self.model = model
        self._headerView = headerView
        self._headerView.setDefaultAlignment(Qt.AlignLeft)
        def setspecs(col, modelcol):
            modelcol.default_width = col.defaultWidth
            modelcol.editor = col.editor
            modelcol.alignment = col.alignment
            modelcol.cantTruncate = col.cantTruncate
        if columns:
            for col in columns:
                modelcol = self.model.column_by_name(col.attrname)
                setspecs(col, modelcol)
        else:
            col = Column('', 100)
            for modelcol in self.model.column_list:
                setspecs(col, modelcol)
        self.model.view = self
        self._headerView.sectionMoved.connect(self.headerSectionMoved)
        self._headerView.sectionResized.connect(self.headerSectionResized)
    
    #--- Public
    def setColumnsWidth(self, widths):
        #`widths` can be None. If it is, then default widths are set.
        columns = self.model.column_list
        if not widths:
            widths = [column.default_width for column in columns]
        for column, width in zip(columns, widths):
            if width == 0: # column was hidden before.
                width = column.default_width
            self._headerView.resizeSection(column.logical_index, width)
    
    def setColumnsOrder(self, columnIndexes):
        if not columnIndexes:
            return
        for destIndex, columnIndex in enumerate(columnIndexes):
            # moveSection takes 2 visual index arguments, so we have to get our visual index first
            visualIndex = self._headerView.visualIndex(columnIndex)
            self._headerView.moveSection(visualIndex, destIndex)
    
    #--- Events
    def headerSectionMoved(self, logicalIndex, oldVisualIndex, newVisualIndex):
        attrname = self.model.column_by_index(logicalIndex).name
        self.model.move_column(attrname, newVisualIndex)
    
    def headerSectionResized(self, logicalIndex, oldSize, newSize):
        attrname = self.model.column_by_index(logicalIndex).name
        self.model.resize_column(attrname, newSize)
    
    #--- model --> view
    def restore_columns(self):
        columns = self.model.ordered_columns
        indexes = [col.logical_index for col in columns]
        self.setColumnsOrder(indexes)
        widths = [col.width for col in self.model.column_list]
        if not any(widths):
            widths = None
        self.setColumnsWidth(widths)
        for column in self.model.column_list:
            visible = self.model.column_is_visible(column.name)
            self._headerView.setSectionHidden(column.logical_index, not visible)
    
    def set_column_visible(self, colname, visible):
        column = self.model.column_by_name(colname)
        self._headerView.setSectionHidden(column.logical_index, not visible)
