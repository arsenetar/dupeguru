# Created By: Virgil Dupras
# Created On: 2009-11-25
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHeaderView


class Column:
    def __init__(
        self,
        attrname,
        default_width,
        editor=None,
        alignment=Qt.AlignLeft,
        cant_truncate=False,
        painter=None,
        resize_to_fit=False,
    ):
        self.attrname = attrname
        self.default_width = default_width
        self.editor = editor
        # See moneyguru #15. Painter attribute was added to allow custom painting of amount value and
        # currency information. Can be used as a pattern for custom painting of any column.
        self.painter = painter
        self.alignment = alignment
        # This is to indicate, during printing, that a column can't have its data truncated.
        self.cant_truncate = cant_truncate
        self.resize_to_fit = resize_to_fit


class Columns:
    def __init__(self, model, columns, header_view):
        self.model = model
        self._header_view = header_view
        self._header_view.setDefaultAlignment(Qt.AlignLeft)

        def setspecs(col, modelcol):
            modelcol.default_width = col.default_width
            modelcol.editor = col.editor
            modelcol.painter = col.painter
            modelcol.resize_to_fit = col.resize_to_fit
            modelcol.alignment = col.alignment
            modelcol.cant_truncate = col.cant_truncate

        if columns:
            for col in columns:
                modelcol = self.model.column_by_name(col.attrname)
                setspecs(col, modelcol)
        else:
            col = Column("", 100)
            for modelcol in self.model.column_list:
                setspecs(col, modelcol)
        self.model.view = self
        self._header_view.sectionMoved.connect(self.header_section_moved)
        self._header_view.sectionResized.connect(self.header_section_resized)

        # See moneyguru #14 and #15.  This was added in order to allow automatic resizing of columns.
        for column in self.model.column_list:
            if column.resize_to_fit:
                self._header_view.setSectionResizeMode(column.logical_index, QHeaderView.ResizeToContents)

    # --- Public
    def set_columns_width(self, widths):
        # `widths` can be None. If it is, then default widths are set.
        columns = self.model.column_list
        if not widths:
            widths = [column.default_width for column in columns]
        for column, width in zip(columns, widths):
            if width == 0:  # column was hidden before.
                width = column.default_width
            self._header_view.resizeSection(column.logical_index, width)

    def set_columns_order(self, column_indexes):
        if not column_indexes:
            return
        for dest_index, column_index in enumerate(column_indexes):
            # moveSection takes 2 visual index arguments, so we have to get our visual index first
            visual_index = self._header_view.visualIndex(column_index)
            self._header_view.moveSection(visual_index, dest_index)

    # --- Events
    def header_section_moved(self, logical_index, old_visual_index, new_visual_index):
        attrname = self.model.column_by_index(logical_index).name
        self.model.move_column(attrname, new_visual_index)

    def header_section_resized(self, logical_index, old_size, new_size):
        attrname = self.model.column_by_index(logical_index).name
        self.model.resize_column(attrname, new_size)

    # --- model --> view
    def restore_columns(self):
        columns = self.model.ordered_columns
        indexes = [col.logical_index for col in columns]
        self.set_columns_order(indexes)
        widths = [col.width for col in self.model.column_list]
        if not any(widths):
            widths = None
        self.set_columns_width(widths)
        for column in self.model.column_list:
            visible = self.model.column_is_visible(column.name)
            self._header_view.setSectionHidden(column.logical_index, not visible)

    def set_column_visible(self, colname, visible):
        column = self.model.column_by_name(colname)
        self._header_view.setSectionHidden(column.logical_index, not visible)
