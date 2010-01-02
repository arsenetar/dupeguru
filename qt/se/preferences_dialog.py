# Created By: Virgil Dupras
# Created On: 2009-05-24
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from PyQt4.QtCore import SIGNAL, Qt
from PyQt4.QtGui import QDialog, QDialogButtonBox

from hsutil.misc import tryint

from core.scanner import SCAN_TYPE_FILENAME, SCAN_TYPE_CONTENT

from preferences_dialog_ui import Ui_PreferencesDialog
import preferences

SCAN_TYPE_ORDER = [
    SCAN_TYPE_FILENAME,
    SCAN_TYPE_CONTENT,
]

class PreferencesDialog(QDialog, Ui_PreferencesDialog):
    def __init__(self, parent, app):
        flags = Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowSystemMenuHint
        QDialog.__init__(self, parent, flags)
        self.app = app
        self._setupUi()
        
        self.connect(self.buttonBox, SIGNAL('clicked(QAbstractButton*)'), self.buttonClicked)
        self.connect(self.scanTypeComboBox, SIGNAL('currentIndexChanged(int)'), self.scanTypeChanged)
    
    def _setupUi(self):
        self.setupUi(self)
    
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
        setchecked(self.useRegexpBox, prefs.use_regexp)
        setchecked(self.removeEmptyFoldersBox, prefs.remove_empty_folders)
        setchecked(self.ignoreSmallFilesBox, prefs.ignore_small_files)
        self.sizeThresholdEdit.setText(unicode(prefs.small_file_threshold))
        self.copyMoveDestinationComboBox.setCurrentIndex(prefs.destination_type)
    
    def save(self):
        prefs = self.app.prefs
        prefs.filter_hardness = self.filterHardnessSlider.value()
        prefs.scan_type = SCAN_TYPE_ORDER[self.scanTypeComboBox.currentIndex()]
        ischecked = lambda cb: cb.checkState() == Qt.Checked
        prefs.match_similar = ischecked(self.matchSimilarBox)
        prefs.word_weighting = ischecked(self.wordWeightingBox)
        prefs.mix_file_kind = ischecked(self.mixFileKindBox)
        prefs.use_regexp = ischecked(self.useRegexpBox)
        prefs.remove_empty_folders = ischecked(self.removeEmptyFoldersBox)
        prefs.ignore_small_files = ischecked(self.ignoreSmallFilesBox)
        prefs.small_file_threshold = tryint(self.sizeThresholdEdit.text())
        prefs.destination_type = self.copyMoveDestinationComboBox.currentIndex()
    
    def resetToDefaults(self):
        self.load(preferences.Preferences())
    
    #--- Events
    def buttonClicked(self, button):
        role = self.buttonBox.buttonRole(button)
        if role == QDialogButtonBox.ResetRole:
            self.resetToDefaults()
    
    def scanTypeChanged(self, index):
        scan_type = SCAN_TYPE_ORDER[self.scanTypeComboBox.currentIndex()]
        word_based = scan_type == SCAN_TYPE_FILENAME
        self.filterHardnessSlider.setEnabled(word_based)
        self.matchSimilarBox.setEnabled(word_based)
        self.wordWeightingBox.setEnabled(word_based)
    
