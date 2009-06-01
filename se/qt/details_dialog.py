#!/usr/bin/env python
# Unit Name: details_dialog
# Created By: Virgil Dupras
# Created On: 2009-05-24
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

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
