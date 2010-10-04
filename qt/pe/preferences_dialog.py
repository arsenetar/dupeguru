# Created By: Virgil Dupras
# Created On: 2009-04-29
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import sys
from PyQt4.QtCore import SIGNAL, Qt, QSize
from PyQt4.QtGui import (QDialog, QDialogButtonBox, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QSlider, QSizePolicy, QSpacerItem, QWidget, QCheckBox, QLineEdit, QDialogButtonBox, QApplication)

from . import preferences

class PreferencesDialog(QDialog):
    def __init__(self, parent, app):
        flags = Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowSystemMenuHint
        QDialog.__init__(self, parent, flags)
        self.app = app
        self._setupUi()
        
        self.connect(self.buttonBox, SIGNAL('clicked(QAbstractButton*)'), self.buttonClicked)
        self.connect(self.filterHardnessSlider, SIGNAL("valueChanged(int)"), self.filterHardnessLabel.setNum)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
    
    def _setupUi(self):
        self.setWindowTitle("Preferences")
        self.resize(304, 263)
        self.setSizeGripEnabled(False)
        self.setModal(True)
        self.verticalLayout_2 = QVBoxLayout(self)
        self.verticalLayout = QVBoxLayout()
        self.horizontalLayout_3 = QHBoxLayout()
        self.label = QLabel(self)
        self.label.setText("Filter Hardness:")
        self.label.setMinimumSize(QSize(0, 0))
        self.horizontalLayout_3.addWidget(self.label)
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setSpacing(0)
        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setSpacing(12)
        self.filterHardnessSlider = QSlider(self)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.filterHardnessSlider.sizePolicy().hasHeightForWidth())
        self.filterHardnessSlider.setSizePolicy(sizePolicy)
        self.filterHardnessSlider.setMinimum(1)
        self.filterHardnessSlider.setMaximum(100)
        self.filterHardnessSlider.setTracking(True)
        self.filterHardnessSlider.setOrientation(Qt.Horizontal)
        self.horizontalLayout_6.addWidget(self.filterHardnessSlider)
        self.filterHardnessLabel = QLabel(self)
        self.filterHardnessLabel.setText("100")
        self.filterHardnessLabel.setMinimumSize(QSize(21, 0))
        self.horizontalLayout_6.addWidget(self.filterHardnessLabel)
        self.verticalLayout_3.addLayout(self.horizontalLayout_6)
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setContentsMargins(-1, 0, -1, -1)
        self.label_4 = QLabel(self)
        self.label_4.setText("More Results")
        self.horizontalLayout_5.addWidget(self.label_4)
        spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem)
        self.label_3 = QLabel(self)
        self.label_3.setText("Fewer Results")
        self.horizontalLayout_5.addWidget(self.label_3)
        self.verticalLayout_3.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_3.addLayout(self.verticalLayout_3)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.matchScaledBox = QCheckBox(self)
        self.matchScaledBox.setText("Match scaled pictures together")
        self.verticalLayout.addWidget(self.matchScaledBox)
        self.mixFileKindBox = QCheckBox(self)
        self.mixFileKindBox.setText("Can mix file kind")
        self.verticalLayout.addWidget(self.mixFileKindBox)
        self.useRegexpBox = QCheckBox(self)
        self.useRegexpBox.setText("Use regular expressions when filtering")
        self.verticalLayout.addWidget(self.useRegexpBox)
        self.removeEmptyFoldersBox = QCheckBox(self)
        self.removeEmptyFoldersBox.setText("Remove empty folders on delete or move")
        self.verticalLayout.addWidget(self.removeEmptyFoldersBox)
        self.ignoreHardlinkMatches = QCheckBox(self)
        self.ignoreHardlinkMatches.setText("Ignore duplicates hardlinking to the same file")
        self.verticalLayout.addWidget(self.ignoreHardlinkMatches)
        self.horizontalLayout_4 = QHBoxLayout()
        self.label_5 = QLabel(self)
        self.label_5.setText("Copy and Move:")
        self.label_5.setMinimumSize(QSize(0, 0))
        self.horizontalLayout_4.addWidget(self.label_5)
        self.copyMoveDestinationComboBox = QComboBox(self)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.copyMoveDestinationComboBox.sizePolicy().hasHeightForWidth())
        self.copyMoveDestinationComboBox.addItem("Right in destination")
        self.copyMoveDestinationComboBox.addItem("Recreate relative path")
        self.copyMoveDestinationComboBox.addItem("Recreate absolute path")
        self.horizontalLayout_4.addWidget(self.copyMoveDestinationComboBox)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.label_2 = QLabel(self)
        self.label_2.setText("Custom Command (arguments: %d for dupe %r for ref):")
        self.verticalLayout.addWidget(self.label_2)
        self.customCommandEdit = QLineEdit(self)
        self.verticalLayout.addWidget(self.customCommandEdit)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok|QDialogButtonBox.RestoreDefaults)
        self.verticalLayout_2.addWidget(self.buttonBox)
        if sys.platform not in {'darwin', 'linux2'}:
            self.verticalLayout.removeWidget(self.ignoreHardlinkMatches)
            self.ignoreHardlinkMatches.setHidden(True)
    
    def load(self, prefs=None):
        if prefs is None:
            prefs = self.app.prefs
        self.filterHardnessSlider.setValue(prefs.filter_hardness)
        self.filterHardnessLabel.setNum(prefs.filter_hardness)
        setchecked = lambda cb, b: cb.setCheckState(Qt.Checked if b else Qt.Unchecked)
        setchecked(self.matchScaledBox, prefs.match_scaled)
        setchecked(self.mixFileKindBox, prefs.mix_file_kind)
        setchecked(self.useRegexpBox, prefs.use_regexp)
        setchecked(self.removeEmptyFoldersBox, prefs.remove_empty_folders)
        self.copyMoveDestinationComboBox.setCurrentIndex(prefs.destination_type)
        self.customCommandEdit.setText(prefs.custom_command)
    
    def save(self):
        prefs = self.app.prefs
        prefs.filter_hardness = self.filterHardnessSlider.value()
        ischecked = lambda cb: cb.checkState() == Qt.Checked
        prefs.match_scaled = ischecked(self.matchScaledBox)
        prefs.mix_file_kind = ischecked(self.mixFileKindBox)
        prefs.use_regexp = ischecked(self.useRegexpBox)
        prefs.remove_empty_folders = ischecked(self.removeEmptyFoldersBox)
        prefs.destination_type = self.copyMoveDestinationComboBox.currentIndex()
        prefs.custom_command = str(self.customCommandEdit.text())
    
    def resetToDefaults(self):
        self.load(preferences.Preferences())
    
    #--- Events
    def buttonClicked(self, button):
        role = self.buttonBox.buttonRole(button)
        if role == QDialogButtonBox.ResetRole:
            self.resetToDefaults()
    

if __name__ == '__main__':
    import sys
    from ..testapp import TestApp
    app = QApplication([])
    dgapp = TestApp()
    dialog = PreferencesDialog(None, dgapp)
    dialog.show()
    sys.exit(app.exec_())