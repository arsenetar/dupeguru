# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-04-12
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QDialog

from core.gui.problem_dialog import ProblemDialog as ProblemDialogModel
from .problem_table import ProblemTable
from .problem_dialog_ui import Ui_ProblemDialog

class ProblemDialog(QDialog, Ui_ProblemDialog):
    def __init__(self, parent, app):
        flags = Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowSystemMenuHint
        QDialog.__init__(self, parent, flags)
        self.app = app
        self._setupUi()
        self.model = ProblemDialogModel(view=self, app=app)
        self.table = ProblemTable(problem_dialog=self, view=self.tableView)
        self.model.connect()
        self.table.model.connect()
        
        self.revealButton.clicked.connect(self.model.reveal_selected_dupe)
    
    def _setupUi(self):
        self.setupUi(self)
    
