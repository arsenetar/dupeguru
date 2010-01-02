# Created By: Virgil Dupras
# Created On: 2009-04-29
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from PyQt4.QtCore import SIGNAL, Qt
from PyQt4.QtGui import QDialog, QDialogButtonBox

from core.scanner import (SCAN_TYPE_FILENAME, SCAN_TYPE_FIELDS, SCAN_TYPE_FIELDS_NO_ORDER,
    SCAN_TYPE_TAG, SCAN_TYPE_CONTENT, SCAN_TYPE_CONTENT_AUDIO)

from preferences_dialog_ui import Ui_PreferencesDialog
import preferences

SCAN_TYPE_ORDER = [
    SCAN_TYPE_FILENAME,
    SCAN_TYPE_FIELDS,
    SCAN_TYPE_FIELDS_NO_ORDER,
    SCAN_TYPE_TAG,
    SCAN_TYPE_CONTENT,
    SCAN_TYPE_CONTENT_AUDIO,
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
        setchecked(self.tagTrackBox, prefs.scan_tag_track)
        setchecked(self.tagArtistBox, prefs.scan_tag_artist)
        setchecked(self.tagAlbumBox, prefs.scan_tag_album)
        setchecked(self.tagTitleBox, prefs.scan_tag_title)
        setchecked(self.tagGenreBox, prefs.scan_tag_genre)
        setchecked(self.tagYearBox, prefs.scan_tag_year)
        setchecked(self.matchSimilarBox, prefs.match_similar)
        setchecked(self.wordWeightingBox, prefs.word_weighting)
        setchecked(self.mixFileKindBox, prefs.mix_file_kind)
        setchecked(self.useRegexpBox, prefs.use_regexp)
        setchecked(self.removeEmptyFoldersBox, prefs.remove_empty_folders)
        self.copyMoveDestinationComboBox.setCurrentIndex(prefs.destination_type)
    
    def save(self):
        prefs = self.app.prefs
        prefs.filter_hardness = self.filterHardnessSlider.value()
        prefs.scan_type = SCAN_TYPE_ORDER[self.scanTypeComboBox.currentIndex()]
        ischecked = lambda cb: cb.checkState() == Qt.Checked
        prefs.scan_tag_track = ischecked(self.tagTrackBox)
        prefs.scan_tag_artist = ischecked(self.tagArtistBox)
        prefs.scan_tag_album = ischecked(self.tagAlbumBox)
        prefs.scan_tag_title = ischecked(self.tagTitleBox)
        prefs.scan_tag_genre = ischecked(self.tagGenreBox)
        prefs.scan_tag_year = ischecked(self.tagYearBox)
        prefs.match_similar = ischecked(self.matchSimilarBox)
        prefs.word_weighting = ischecked(self.wordWeightingBox)
        prefs.mix_file_kind = ischecked(self.mixFileKindBox)
        prefs.use_regexp = ischecked(self.useRegexpBox)
        prefs.remove_empty_folders = ischecked(self.removeEmptyFoldersBox)
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
        word_based = scan_type in [SCAN_TYPE_FILENAME, SCAN_TYPE_FIELDS, SCAN_TYPE_FIELDS_NO_ORDER,
            SCAN_TYPE_TAG]
        tag_based = scan_type == SCAN_TYPE_TAG
        self.filterHardnessSlider.setEnabled(word_based)
        self.matchSimilarBox.setEnabled(word_based)
        self.wordWeightingBox.setEnabled(word_based)
        self.tagTrackBox.setEnabled(tag_based)
        self.tagArtistBox.setEnabled(tag_based)
        self.tagAlbumBox.setEnabled(tag_based)
        self.tagTitleBox.setEnabled(tag_based)
        self.tagGenreBox.setEnabled(tag_based)
        self.tagYearBox.setEnabled(tag_based)
    
