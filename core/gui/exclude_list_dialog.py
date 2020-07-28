# Created On: 2012/03/13
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

# from hscommon.trans import tr
from .exclude_list_table import ExcludeListTable

default_regexes = [".*thumbs", "\.DS.Store", "\.Trash", "Trash-Bin"]


class ExcludeListDialogCore:
    # --- View interface
    # show()
    #

    def __init__(self, app):
        self.app = app
        self.exclude_list = self.app.exclude_list  # Markable from exclude.py
        self.exclude_list_table = ExcludeListTable(self, app)  # GUITable, this is the "model"

    def restore_defaults(self):
        for _, regex in self.exclude_list:
            if regex not in default_regexes:
                self.exclude_list.unmark(regex)
        for default_regex in default_regexes:
            if not self.exclude_list.isExcluded(default_regex):
                self.exclude_list.add(default_regex)
                self.exclude_list.mark(default_regex)
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
            print(f"dupeGuru Warning: {e}")
        return False

    def add(self, regex):
        self.exclude_list.add(regex)
        self.exclude_list.mark(regex)
        # TODO make checks here before adding to GUI
        self.exclude_list_table.add(regex)

    def show(self):
        self.view.show()
