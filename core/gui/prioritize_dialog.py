# Created By: Virgil Dupras
# Created On: 2011-09-06
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hscommon.gui.selectable_list import GUISelectableList

from ..prioritize import all_categories

class CriterionCategoryList(GUISelectableList):
    def __init__(self, dialog):
        self.dialog = dialog
        GUISelectableList.__init__(self, [c.NAME for c in dialog.categories])
    
    def _update_selection(self):
        self.dialog.select_category(self.dialog.categories[self.selected_index])


class PrioritizeDialog:
    def __init__(self, view, app):
        self.app = app
        self.categories = [cat(app.results) for cat in all_categories()]
        self.category_list = CriterionCategoryList(self)
        self.criteria = []
        self.criteria_list = GUISelectableList()
        self.prioritizations = []
        self.prioritization_list = GUISelectableList()
    
    #--- Private
    def _sort_key(self, dupe):
        return tuple(crit.sort_key(dupe) for crit in self.prioritizations)
    
    #--- Public
    def select_category(self, category):
        self.criteria = category.criteria_list()
        self.criteria_list[:] = [c.display_value for c in self.criteria]

    def add_selected(self):
        # Add selected criteria in criteria_list to prioritization_list.
        crit = self.criteria[self.criteria_list.selected_index]
        self.prioritizations.append(crit)
        self.prioritization_list[:] = [crit.display for crit in self.prioritizations]
    
    def perform_reprioritization(self):
        self.app.reprioritize_groups(self._sort_key)
