# Created By: Virgil Dupras
# Created On: 2009-05-09
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from hashlib import md5

from PyQt4.QtGui import QDialog

from reg_submit_dialog import RegSubmitDialog
from reg_demo_dialog import RegDemoDialog

class Registration(object):
    def __init__(self, app):
        self.app = app
    
    def ask_for_code(self):
        dialog = RegSubmitDialog(self.app.main_window, self.app.is_code_valid)
        result = dialog.exec_()
        code = unicode(dialog.codeEdit.text())
        email = unicode(dialog.emailEdit.text())
        dialog.setParent(None) # free it
        if result == QDialog.Accepted and self.app.is_code_valid(code, email):
            self.app.set_registration(code, email)
            return True
        return False
    
    def show_nag(self):
        dialog = RegDemoDialog(self.app.main_window, self)
        dialog.exec_()
        dialog.setParent(None) # free it
    
