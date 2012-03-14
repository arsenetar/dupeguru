# Created On: 2012/03/13
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hscommon.trans import tr
from .ignore_list_table import IgnoreListTable

class IgnoreListDialog:
    #--- View interface
    # show()
    #
    
    def __init__(self, app):
        self.app = app
        self.ignore_list = self.app.scanner.ignore_list
        self.ignore_list_table = IgnoreListTable(self)
    
    def clear(self):
        if not self.ignore_list:
            return
        msg = tr("Do you really want to remove all %d items from the ignore list?") % len(self.ignore_list)
        if self.app.view.ask_yes_no(msg):
            self.ignore_list.Clear()
            self.refresh()
    
    def refresh(self):
        self.ignore_list_table.refresh()
    
    def remove_selected(self):
        for row in self.ignore_list_table.selected_rows:
            self.ignore_list.remove(row.path1_original, row.path2_original)
        self.refresh()
    
    def show(self):
        self.view.show()
    
