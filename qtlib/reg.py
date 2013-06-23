# Created By: Virgil Dupras
# Created On: 2009-05-09
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4.QtGui import QDialog

from .reg_submit_dialog import RegSubmitDialog
from .reg_demo_dialog import RegDemoDialog

class Registration:
    def __init__(self, app):
        self.app = app
    
    def ask_for_code(self):
        dialog = RegSubmitDialog(None, self)
        return dialog.exec_() == QDialog.Accepted
    
    def show_demo_nag(self, prompt):
        dialog = RegDemoDialog(None, self, prompt)
        dialog.exec_()
    
