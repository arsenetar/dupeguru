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
        self.categories = [KindCategory(app.results)]
        self.category_list = CriterionCategoryList(self)
        self.criteria_list = []
    
    def select_category(self, category):
        criteria = category.criteria_list()
        self.criteria_list = [c.value for c in criteria]
