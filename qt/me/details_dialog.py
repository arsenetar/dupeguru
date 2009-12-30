# Created By: Virgil Dupras
# Created On: 2009-04-27
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QDialog

from base.details_table import DetailsModel
from details_dialog_ui import Ui_DetailsDialog

class DetailsDialog(QDialog, Ui_DetailsDialog):
    def __init__(self, parent, app):
        QDialog.__init__(self, parent, Qt.Tool)
        self.app = app
        self.setupUi(self)
        self.model = DetailsModel(app)
        self.tableView.setModel(self.model)
