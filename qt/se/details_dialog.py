# Created By: Virgil Dupras
# Created On: 2009-05-24
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from base.details_dialog import DetailsDialog as DetailsDialogBase
from details_dialog_ui import Ui_DetailsDialog

class DetailsDialog(DetailsDialogBase, Ui_DetailsDialog):
    def _setupUi(self):
        self.setupUi(self)
    
