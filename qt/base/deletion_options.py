# Created By: Virgil Dupras
# Created On: 2012-05-30
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QDialog, QVBoxLayout, QLabel, QCheckBox, QDialogButtonBox

from hscommon.plat import ISOSX, ISLINUX
from hscommon.trans import trget
from qtlib.radio_box import RadioBox

tr = trget('ui')

class DeletionOptions(QDialog):
    def __init__(self, parent, model):
        flags = Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowSystemMenuHint
        QDialog.__init__(self, parent, flags)
        self._setupUi()
        self.model = model
        self.model.view = self
        
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
    
    def _setupUi(self):
        self.setWindowTitle(tr("Deletion Options"))
        self.resize(400, 270)
        self.verticalLayout = QVBoxLayout(self)
        self.msgLabel = QLabel()
        self.verticalLayout.addWidget(self.msgLabel)
        self.linkCheckbox = QCheckBox(tr("Link deleted files"))
        self.verticalLayout.addWidget(self.linkCheckbox)
        text = tr("After having deleted a duplicate, place a link targeting the reference file "
            "to replace the deleted file.")
        self.linkMessageLabel = QLabel(text)
        self.linkMessageLabel.setWordWrap(True)
        self.verticalLayout.addWidget(self.linkMessageLabel)
        self.linkTypeRadio = RadioBox(items=[tr("Symlink"), tr("Hardlink")], spread=False)
        self.verticalLayout.addWidget(self.linkTypeRadio)
        if not (ISOSX or ISLINUX):
            self.linkCheckbox.setEnabled(False)
            self.linkTypeRadio.setEnabled(False)
            self.linkCheckbox.setText(self.linkCheckbox.text() + tr(" (Mac OS X or Linux only)"))
        self.directCheckbox = QCheckBox(tr("Directly delete files"))
        self.verticalLayout.addWidget(self.directCheckbox)
        text = tr("Instead of sending files to trash, delete them directly. This option is usually "
            "used as a workaround when the normal deletion method doesn't work.")
        self.directMessageLabel = QLabel(text)
        self.directMessageLabel.setWordWrap(True)
        self.verticalLayout.addWidget(self.directMessageLabel)
        self.buttonBox = QDialogButtonBox()
        self.buttonBox.addButton(tr("Proceed"), QDialogButtonBox.AcceptRole)
        self.buttonBox.addButton(tr("Cancel"), QDialogButtonBox.RejectRole)
        self.verticalLayout.addWidget(self.buttonBox)
    
    #--- model --> view
    def update_msg(self, msg):
        self.msgLabel.setText(msg)
    
    def show(self):
        self.linkCheckbox.setChecked(self.model.link_deleted)
        self.linkTypeRadio.selected_index = 1 if self.model.use_hardlinks else 0
        self.directCheckbox.setChecked(self.model.direct)
        result = self.exec()
        self.model.link_deleted = self.linkCheckbox.isChecked()
        self.model.use_hardlinks = self.linkTypeRadio.selected_index == 1
        self.model.direct = self.directCheckbox.isChecked()
        return result == QDialog.Accepted
    
