# Created By: Virgil Dupras
# Created On: 2009-04-27
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QVBoxLayout, QAbstractItemView

from hscommon.trans import trget
from ..base.details_dialog import DetailsDialog as DetailsDialogBase
from ..base.details_table import DetailsTable

tr = trget('ui')

class DetailsDialog(DetailsDialogBase):
    def _setupUi(self):
        self.setWindowTitle(tr("Details"))
        self.resize(502, 295)
        self.setMinimumSize(QSize(250, 250))
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.tableView = DetailsTable(self)
        self.tableView.setAlternatingRowColors(True)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableView.setShowGrid(False)
        self.verticalLayout.addWidget(self.tableView)
    
