# Created By: Virgil Dupras
# Created On: 2011-09-06
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hscommon.gui.selectable_list import SelectableList

from ..prioritize import KindCategory

class CriterionCategoryList(SelectableList):
    def __init__(self, dialog):
        self.dialog = dialog
        SelectableList.__init__(self, [c.NAME for c in dialog.categories])
    
    def _update_selection(self):
        self.dialog.select_category(self.dialog.categories[self.selected_index])


class PrioritizeDialog:
    def __init__(self, view, app):
        self.app = app
        self.categories = [KindCategory(app.results)]
        self.category_list = CriterionCategoryList(self)
        self.criteria = []
        self.criteria_list = SelectableList()
        self.prioritizations = []
    
    #--- Private
    def _sort_key(self, dupe):
        # Our sort key consists of a tuple of inverted bool values represented as ints. When a dupe
        # fits a criteria, we want it at the top of the listm and thus we'll give it the value 0.
        # When the dupe doesn't fit a criteria, we ant it at the bottom, and we give the value 1.
        result = (crit.test_dupe(dupe) for crit in self.prioritizations)
        return tuple((0 if value else 1) for value in result)
    
    #--- Public
    def select_category(self, category):
        self.criteria = category.criteria_list()
        self.criteria_list[:] = [c.value for c in self.criteria]

    def add_selected(self):
        # Add selected criteria in criteria_list to prioritization_list.
        crit = self.criteria[self.criteria_list.selected_index]
        self.prioritizations.append(crit)
    
    def perform_reprioritization(self):
        self.app.reprioritize_groups(self._sort_key)
