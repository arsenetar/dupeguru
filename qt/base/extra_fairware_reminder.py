# Created By: Virgil Dupras
# Created On: 2011-03-04
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import sys

from PyQt4.QtCore import Qt, QUrl, QTimer
from PyQt4.QtGui import (QDialog, QDesktopServices, QApplication, QVBoxLayout, QHBoxLayout, QLabel,
    QFont, QSpacerItem, QSizePolicy, QPushButton)

from hscommon.plat import ISLINUX
from hscommon.trans import trget
from core.gui.extra_fairware_reminder import ExtraFairwareReminder as ExtraFairwareReminderModel

tr = trget('ui')

class ExtraFairwareReminder(QDialog):
    def __init__(self, parent, app):
        flags = Qt.CustomizeWindowHint | Qt.WindowTitleHint
        QDialog.__init__(self, parent, flags)
        self.setModal(True)
        self.app = app
        self.model = ExtraFairwareReminderModel(self, app)
        self._setupUi()
        
        self.continueButton.setEnabled(False)
        self.continueButton.clicked.connect(self.accept)
        self.contributeButton.clicked.connect(self.contributeClicked)
        self.model.start()
    
    def _setupUi(self):
        self.setWindowTitle(tr("Sorry, I must insist"))
        dlg_height = 410 if ISLINUX else 330
        self.resize(380, dlg_height)
        self.verticalLayout = QVBoxLayout(self)
        self.descLabel = QLabel(self)        
        self.descLabel.setText(tr("ExtraFairwarePromptMsg"))
        self.descLabel.setWordWrap(True)
        self.verticalLayout.addWidget(self.descLabel)
        self.reasonLabel = QLabel(self)        
        self.reasonLabel.setText(tr("ExtraFairwareReasonMsg"))
        self.reasonLabel.setWordWrap(True)
        font = QFont()
        font.setWeight(75)
        font.setBold(True)
        self.reasonLabel.setFont(font)
        self.verticalLayout.addWidget(self.reasonLabel)
        self.horizontalLayout = QHBoxLayout()
        spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.contributeButton = QPushButton(self)
        self.contributeButton.setText(tr("Contribute"))
        self.horizontalLayout.addWidget(self.contributeButton)
        self.continueButton = QPushButton(self)
        self.continueButton.setText(tr("Continue"))
        self.horizontalLayout.addWidget(self.continueButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
    
    #--- model --> view
    def start_timer(self):
        self._timer = QTimer()
        self._timer.setInterval(200)
        self._timer.timeout.connect(self.model.update_button)
        self._timer.start()
    
    def stop_timer(self):
        self._timer.stop()
        del self._timer
    
    def enable_button(self):
        self.continueButton.setEnabled(True)
    
    def set_button_text(self, text):
        self.continueButton.setText(text)
    
    #--- Events
    def contributeClicked(self):
        url = QUrl('http://open.hardcoded.net/contribute/')
        QDesktopServices.openUrl(url)
    

if __name__ == '__main__':
    app = QApplication([])
    class FakeReg:
        app = app
    dialog = ExtraFairwareReminder(None, FakeReg())
    dialog.show()
    sys.exit(app.exec_())
