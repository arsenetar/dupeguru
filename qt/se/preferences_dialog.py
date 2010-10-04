# Created By: Virgil Dupras
# Created On: 2009-05-24
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import platform
from PyQt4.QtCore import SIGNAL, Qt, QSize
from PyQt4.QtGui import (QDialog, QDialogButtonBox, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QSlider, QSizePolicy, QSpacerItem, QWidget, QCheckBox, QLineEdit, QDialogButtonBox, QApplication)

from hsutil.misc import tryint

from core.scanner import ScanType

from . import preferences

SCAN_TYPE_ORDER = [
    ScanType.Filename,
    ScanType.Contents,
]

class PreferencesDialog(QDialog):
    def __init__(self, parent, app):
        flags = Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowSystemMenuHint
        QDialog.__init__(self, parent, flags)
        self.app = app
        self._setupUi()
        
        self.connect(self.buttonBox, SIGNAL('clicked(QAbstractButton*)'), self.buttonClicked)
        self.connect(self.scanTypeComboBox, SIGNAL('currentIndexChanged(int)'), self.scanTypeChanged)
        self.connect(self.filterHardnessSlider, SIGNAL("valueChanged(int)"), self.filterHardnessLabel.setNum)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
    
    def _setupUi(self):
        self.setWindowTitle("Preferences")
        self.resize(308, 361)
        self.setSizeGripEnabled(False)
        self.setModal(True)
        self.verticalLayout_2 = QVBoxLayout(self)
        self.verticalLayout = QVBoxLayout()
        self.horizontalLayout = QHBoxLayout()
        self.label_2 = QLabel(self)
        self.label_2.setText("Scan Type:")
        self.label_2.setMinimumSize(QSize(100, 0))
        self.label_2.setMaximumSize(QSize(100, 16777215))
        self.horizontalLayout.addWidget(self.label_2)
        self.scanTypeComboBox = QComboBox(self)
        self.scanTypeComboBox.addItem("Filename")
        self.scanTypeComboBox.addItem("Contents")
        self.horizontalLayout.addWidget(self.scanTypeComboBox)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_3 = QHBoxLayout()
        self.label = QLabel(self)
        self.label.setText("Filter Hardness:")
        self.label.setMinimumSize(QSize(100, 0))
        self.label.setMaximumSize(QSize(100, 16777215))
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
        self.widget = QWidget(self)
        self.widget.setMinimumSize(QSize(0, 136))
        self.verticalLayout_4 = QVBoxLayout(self.widget)
        self.wordWeightingBox = QCheckBox(self.widget)
        self.wordWeightingBox.setText("Word weighting")
        self.verticalLayout_4.addWidget(self.wordWeightingBox)
        self.matchSimilarBox = QCheckBox(self.widget)
        self.matchSimilarBox.setText("Match similar words")
        self.verticalLayout_4.addWidget(self.matchSimilarBox)
        self.mixFileKindBox = QCheckBox(self.widget)
        self.mixFileKindBox.setText("Can mix file kind")
        self.verticalLayout_4.addWidget(self.mixFileKindBox)
        self.useRegexpBox = QCheckBox(self.widget)
        self.useRegexpBox.setText("Use regular expressions when filtering")
        self.verticalLayout_4.addWidget(self.useRegexpBox)
        self.removeEmptyFoldersBox = QCheckBox(self.widget)
        self.removeEmptyFoldersBox.setText("Remove empty folders on delete or move")
        self.verticalLayout_4.addWidget(self.removeEmptyFoldersBox)
        self.horizontalLayout_2 = QHBoxLayout()
        self.ignoreSmallFilesBox = QCheckBox(self.widget)
        self.ignoreSmallFilesBox.setText("Ignore files smaller than")
        self.horizontalLayout_2.addWidget(self.ignoreSmallFilesBox)
        self.sizeThresholdEdit = QLineEdit(self.widget)
        sizePolicy = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizeThresholdEdit.sizePolicy().hasHeightForWidth())
        self.sizeThresholdEdit.setSizePolicy(sizePolicy)
        self.sizeThresholdEdit.setMaximumSize(QSize(50, 16777215))
        self.horizontalLayout_2.addWidget(self.sizeThresholdEdit)
        self.label_6 = QLabel(self.widget)
        self.label_6.setText("KB")
        self.horizontalLayout_2.addWidget(self.label_6)
        spacerItem1 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.verticalLayout_4.addLayout(self.horizontalLayout_2)
        self.ignoreHardlinkMatches = QCheckBox(self.widget)
        self.ignoreHardlinkMatches.setText("Ignore duplicates hardlinking to the same file")
        self.verticalLayout_4.addWidget(self.ignoreHardlinkMatches)
        self.verticalLayout.addWidget(self.widget)
        self.horizontalLayout_4 = QHBoxLayout()
        self.label_5 = QLabel(self)
        self.label_5.setText("Copy and Move:")
        self.label_5.setMinimumSize(QSize(100, 0))
        self.label_5.setMaximumSize(QSize(100, 16777215))
        self.horizontalLayout_4.addWidget(self.label_5)
        self.copyMoveDestinationComboBox = QComboBox(self)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.copyMoveDestinationComboBox.sizePolicy().hasHeightForWidth())
        self.copyMoveDestinationComboBox.setSizePolicy(sizePolicy)
        self.copyMoveDestinationComboBox.addItem("Right in destination")
        self.copyMoveDestinationComboBox.addItem("Recreate relative path")
        self.copyMoveDestinationComboBox.addItem("Recreate absolute path")
        self.horizontalLayout_4.addWidget(self.copyMoveDestinationComboBox)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.label_7 = QLabel(self)
        self.label_7.setText("Custom Command (arguments: %d for dupe, %r for ref):")
        self.verticalLayout.addWidget(self.label_7)
        self.customCommandEdit = QLineEdit(self)
        self.verticalLayout.addWidget(self.customCommandEdit)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok|QDialogButtonBox.RestoreDefaults)
        self.verticalLayout_2.addWidget(self.buttonBox)
        
        if platform.system() not in {'Darwin', 'Linux'}:
            self.verticalLayout_4.removeWidget(self.ignoreHardlinkMatches)
            self.ignoreHardlinkMatches.setHidden(True)
        if platform.system() == 'Linux':
            # Under linux, whether it's a Qt layout bug or something else, the size threshold text edit
            # doesn't have enough space, so we make the pref pane higher to compensate.
            self.resize(self.width(), 400)
    
    def load(self, prefs=None):
        if prefs is None:
            prefs = self.app.prefs
        self.filterHardnessSlider.setValue(prefs.filter_hardness)
        self.filterHardnessLabel.setNum(prefs.filter_hardness)
        scan_type_index = SCAN_TYPE_ORDER.index(prefs.scan_type)
        self.scanTypeComboBox.setCurrentIndex(scan_type_index)
        setchecked = lambda cb, b: cb.setCheckState(Qt.Checked if b else Qt.Unchecked)
        setchecked(self.matchSimilarBox, prefs.match_similar)
        setchecked(self.wordWeightingBox, prefs.word_weighting)
        setchecked(self.mixFileKindBox, prefs.mix_file_kind)
        setchecked(self.ignoreHardlinkMatches, prefs.ignore_hardlink_matches)
        setchecked(self.useRegexpBox, prefs.use_regexp)
        setchecked(self.removeEmptyFoldersBox, prefs.remove_empty_folders)
        setchecked(self.ignoreSmallFilesBox, prefs.ignore_small_files)
        self.sizeThresholdEdit.setText(str(prefs.small_file_threshold))
        self.copyMoveDestinationComboBox.setCurrentIndex(prefs.destination_type)
        self.customCommandEdit.setText(prefs.custom_command)
    
    def save(self):
        prefs = self.app.prefs
        prefs.filter_hardness = self.filterHardnessSlider.value()
        prefs.scan_type = SCAN_TYPE_ORDER[self.scanTypeComboBox.currentIndex()]
        ischecked = lambda cb: cb.checkState() == Qt.Checked
        prefs.match_similar = ischecked(self.matchSimilarBox)
        prefs.word_weighting = ischecked(self.wordWeightingBox)
        prefs.mix_file_kind = ischecked(self.mixFileKindBox)
        prefs.ignore_hardlink_matches = ischecked(self.ignoreHardlinkMatches)
        prefs.use_regexp = ischecked(self.useRegexpBox)
        prefs.remove_empty_folders = ischecked(self.removeEmptyFoldersBox)
        prefs.ignore_small_files = ischecked(self.ignoreSmallFilesBox)
        prefs.small_file_threshold = tryint(self.sizeThresholdEdit.text())
        prefs.destination_type = self.copyMoveDestinationComboBox.currentIndex()
        prefs.custom_command = str(self.customCommandEdit.text())
    
    def resetToDefaults(self):
        self.load(preferences.Preferences())
    
    #--- Events
    def buttonClicked(self, button):
        role = self.buttonBox.buttonRole(button)
        if role == QDialogButtonBox.ResetRole:
            self.resetToDefaults()
    
    def scanTypeChanged(self, index):
        scan_type = SCAN_TYPE_ORDER[self.scanTypeComboBox.currentIndex()]
        word_based = scan_type == ScanType.Filename
        self.filterHardnessSlider.setEnabled(word_based)
        self.matchSimilarBox.setEnabled(word_based)
        self.wordWeightingBox.setEnabled(word_based)
    

if __name__ == '__main__':
    import sys
    from ..testapp import TestApp
    app = QApplication([])
    dgapp = TestApp()
    dialog = PreferencesDialog(None, dgapp)
    dialog.show()
    sys.exit(app.exec_())