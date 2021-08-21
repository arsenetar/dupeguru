# Created On: 2012/03/13
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from .exclude_list_table import ExcludeListTable
from core.exclude import has_sep
from os import sep
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
        """Rename the selected regex to ``newregex``.
        If there is more than one selected row, the first one is used.
        :param str newregex: The regex to rename the row's regex to.
        :return bool: true if success, false if error.
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
        self.exclude_list.add(regex)
        self.exclude_list.mark(regex)
        self.exclude_list_table.add(regex)

    def test_string(self, test_string):
        """Set the highlight property on each row when its regex matches the
        test_string supplied. Return True if any row matched."""
        matched = False
        for row in self.exclude_list_table.rows:
            compiled_regex = self.exclude_list.get_compiled(row.regex)

            if self.is_match(test_string, compiled_regex):
                row.highlight = True
                matched = True
            else:
                row.highlight = False
        return matched

    def is_match(self, test_string, compiled_regex):
        # This method is like an inverted version of ExcludeList.is_excluded()
        if not compiled_regex:
            return False
        matched = False

        # Test only the filename portion of the path
        if not has_sep(compiled_regex.pattern) and sep in test_string:
            filename = test_string.rsplit(sep, 1)[1]
            if compiled_regex.fullmatch(filename):
                matched = True
            return matched

        # Test the entire path + filename
        if compiled_regex.fullmatch(test_string):
            matched = True
        return matched

    def reset_rows_highlight(self):
        for row in self.exclude_list_table.rows:
            row.highlight = False

    def show(self):
        self.view.show()
