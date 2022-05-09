# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QFontMetrics, QIcon, QColor

from qt.column import Column
from qt.table import Table
from hscommon.trans import trget

tr = trget("ui")


class ExcludeListTable(Table):
    """Model for exclude list"""

    COLUMNS = [Column("marked", default_width=15), Column("regex", default_width=230)]

    def __init__(self, app, view, **kwargs):
        model = app.model.exclude_list_dialog.exclude_list_table  # pointer to GUITable
        super().__init__(model, view, **kwargs)
        font = view.font()
        font.setPointSize(app.prefs.tableFontSize)
        view.setFont(font)
        fm = QFontMetrics(font)
        view.verticalHeader().setDefaultSectionSize(fm.height() + 2)

    def _getData(self, row, column, role):
        if column.name == "marked":
            if role == Qt.CheckStateRole and row.markable:
                return Qt.Checked if row.marked else Qt.Unchecked
            if role == Qt.ToolTipRole and not row.markable:
                return tr("Compilation error: ") + row.get_cell_value("error")
            if role == Qt.DecorationRole and not row.markable:
                return QIcon.fromTheme("dialog-error", QIcon(":/error"))
            return None
        if role == Qt.DisplayRole:
            return row.data[column.name]
        elif role == Qt.FontRole:
            return QFont(self.view.font())
        elif role == Qt.BackgroundRole and column.name == "regex":
            if row.highlight:
                return QColor(10, 200, 10)  # green
        elif role == Qt.EditRole and column.name == "regex":
            return row.data[column.name]
        return None

    def _getFlags(self, row, column):
        flags = Qt.ItemIsEnabled
        if column.name == "marked":
            if row.markable:
                flags |= Qt.ItemIsUserCheckable
        elif column.name == "regex":
            flags |= Qt.ItemIsEditable | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled
        return flags

    def _setData(self, row, column, value, role):
        if role == Qt.CheckStateRole:
            if column.name == "marked":
                row.marked = bool(value)
                return True
        elif role == Qt.EditRole and column.name == "regex":
            return self.model.rename_selected(value)
        return False
