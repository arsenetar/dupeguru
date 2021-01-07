# Created By: Virgil Dupras
# Created On: 2011-09-06
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from hscommon.gui.base import GUIObject
from hscommon.gui.selectable_list import GUISelectableList


class CriterionCategoryList(GUISelectableList):
    def __init__(self, dialog):
        self.dialog = dialog
        GUISelectableList.__init__(self, [c.NAME for c in dialog.categories])

    def _update_selection(self):
        self.dialog.select_category(self.dialog.categories[self.selected_index])
        GUISelectableList._update_selection(self)


class PrioritizationList(GUISelectableList):
    def __init__(self, dialog):
        self.dialog = dialog
        GUISelectableList.__init__(self)

    def _refresh_contents(self):
        self[:] = [crit.display for crit in self.dialog.prioritizations]

    def move_indexes(self, indexes, dest_index):
        indexes.sort()
        prilist = self.dialog.prioritizations
        selected = [prilist[i] for i in indexes]
        for i in reversed(indexes):
            del prilist[i]
        prilist[dest_index:dest_index] = selected
        self._refresh_contents()

    def remove_selected(self):
        prilist = self.dialog.prioritizations
        for i in sorted(self.selected_indexes, reverse=True):
            del prilist[i]
        self._refresh_contents()


class PrioritizeDialog(GUIObject):
    def __init__(self, app):
        GUIObject.__init__(self)
        self.app = app
        self.categories = [cat(app.results) for cat in app._prioritization_categories()]
        self.category_list = CriterionCategoryList(self)
        self.criteria = []
        self.criteria_list = GUISelectableList()
        self.prioritizations = []
        self.prioritization_list = PrioritizationList(self)

    # --- Override
    def _view_updated(self):
        self.category_list.select(0)

    # --- Private
    def _sort_key(self, dupe):
        return tuple(crit.sort_key(dupe) for crit in self.prioritizations)

    # --- Public
    def select_category(self, category):
        self.criteria = category.criteria_list()
        self.criteria_list[:] = [c.display_value for c in self.criteria]

    def add_selected(self):
        # Add selected criteria in criteria_list to prioritization_list.
        if self.criteria_list.selected_index is None:
            return
        for i in self.criteria_list.selected_indexes:
            crit = self.criteria[i]
            self.prioritizations.append(crit)
            del crit
        self.prioritization_list[:] = [crit.display for crit in self.prioritizations]

    def remove_selected(self):
        self.prioritization_list.remove_selected()
        self.prioritization_list.select([])

    def perform_reprioritization(self):
        self.app.reprioritize_groups(self._sort_key)
