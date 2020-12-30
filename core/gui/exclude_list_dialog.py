# Created On: 2012/03/13
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

# from hscommon.trans import tr
from .exclude_list_table import ExcludeListTable
import logging


class ExcludeListDialogCore:
    def __init__(self, app):
        self.app = app
        self.exclude_list = self.app.exclude_list  # Markable from exclude.py
        self.exclude_list_table = ExcludeListTable(self, app)  # GUITable, this is the "model"

    def restore_defaults(self):
        self.exclude_list.restore_defaults()
        self.refresh()

    def refresh(self):
        self.exclude_list_table.refresh()

    def remove_selected(self):
        for row in self.exclude_list_table.selected_rows:
            self.exclude_list_table.remove(row)
            self.exclude_list.remove(row.regex)
        self.refresh()

    def rename_selected(self, newregex):
        """Renames the selected regex to ``newregex``.
        If there's more than one selected row, the first one is used.
        :param str newregex: The regex to rename the row's regex to.
        """
        try:
            r = self.exclude_list_table.selected_rows[0]
            self.exclude_list.rename(r.regex, newregex)
            self.refresh()
            return True
        except Exception as e:
            logging.warning(f"Error while renaming regex to {newregex}: {e}")
        return False

    def add(self, regex):
        try:
            self.exclude_list.add(regex)
        except Exception as e:
            raise(e)
        self.exclude_list.mark(regex)
        self.exclude_list_table.add(regex)

    def test_string(self, test_string):
        """Sets property on row to highlight if its regex matches test_string supplied."""
        matched = False
        for row in self.exclude_list_table.rows:
            compiled_regex = self.exclude_list.get_compiled(row.regex)
            if compiled_regex and compiled_regex.match(test_string):
                matched = True
                row.highlight = True
            else:
                row.highlight = False
        return matched

    def reset_rows_highlight(self):
        for row in self.exclude_list_table.rows:
            row.highlight = False

    def show(self):
        self.view.show()
