# Created By: Virgil Dupras
# Created On: 2009-04-29
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import sys
from PyQt4.QtCore import SIGNAL, QSize
from PyQt4.QtGui import (QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QSizePolicy, QSpacerItem,
    QWidget, QApplication)

from hscommon.trans import tr
from core.scanner import ScanType

from ..base.preferences_dialog import PreferencesDialogBase
from . import preferences

SCAN_TYPE_ORDER = [
    ScanType.Filename,
    ScanType.Fields,
    ScanType.FieldsNoOrder,
    ScanType.Tag,
    ScanType.Contents,
    ScanType.ContentsAudio,
]

class PreferencesDialog(PreferencesDialogBase):
    def __init__(self, parent, app):
        PreferencesDialogBase.__init__(self, parent, app)
        
        self.connect(self.scanTypeComboBox, SIGNAL('currentIndexChanged(int)'), self.scanTypeChanged)
    
    def _setupPreferenceWidgets(self):
        self.horizontalLayout = QHBoxLayout()
        self.label_2 = QLabel(self)
        self.label_2.setText(tr("Scan Type:"))
        self.label_2.setMinimumSize(QSize(100, 0))
        self.label_2.setMaximumSize(QSize(100, 16777215))
        self.horizontalLayout.addWidget(self.label_2)
        self.scanTypeComboBox = QComboBox(self)
        self.scanTypeComboBox.addItem(tr("Filename"))
        self.scanTypeComboBox.addItem(tr("Filename - Fields"))
        self.scanTypeComboBox.addItem(tr("Filename - Fields (No Order)"))
        self.scanTypeComboBox.addItem(tr("Tags"))
        self.scanTypeComboBox.addItem(tr("Contents"))
        self.scanTypeComboBox.addItem(tr("Audio Contents"))
        self.horizontalLayout.addWidget(self.scanTypeComboBox)
        self.widgetsVLayout.addLayout(self.horizontalLayout)
        self._setupFilterHardnessBox()
        self.widgetsVLayout.addLayout(self.filterHardnessHLayout)
        self.widget = QWidget(self)
        self.widget.setMinimumSize(QSize(0, 40))
        self.verticalLayout_4 = QVBoxLayout(self.widget)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setMargin(0)
        self.label_6 = QLabel(self.widget)
        self.label_6.setText(tr("Tags to scan:"))
        self.verticalLayout_4.addWidget(self.label_6)
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setSpacing(0)
        spacerItem1 = QSpacerItem(15, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self._setupAddCheckbox('tagTrackBox', tr("Track"), self.widget)
        self.horizontalLayout_2.addWidget(self.tagTrackBox)
        self._setupAddCheckbox('tagArtistBox', tr("Artist"), self.widget)
        self.horizontalLayout_2.addWidget(self.tagArtistBox)
        self._setupAddCheckbox('tagAlbumBox', tr("Album"), self.widget)
        self.horizontalLayout_2.addWidget(self.tagAlbumBox)
        self._setupAddCheckbox('tagTitleBox', tr("Title"), self.widget)
        self.horizontalLayout_2.addWidget(self.tagTitleBox)
        self._setupAddCheckbox('tagGenreBox', tr("Genre"), self.widget)
        self.horizontalLayout_2.addWidget(self.tagGenreBox)
        self._setupAddCheckbox('tagYearBox', tr("Year"), self.widget)
        self.horizontalLayout_2.addWidget(self.tagYearBox)
        self.verticalLayout_4.addLayout(self.horizontalLayout_2)
        self.widgetsVLayout.addWidget(self.widget)
        self._setupAddCheckbox('wordWeightingBox', tr("Word weighting"))
        self.widgetsVLayout.addWidget(self.wordWeightingBox)
        self._setupAddCheckbox('matchSimilarBox', tr("Match similar words"))
        self.widgetsVLayout.addWidget(self.matchSimilarBox)
        self._setupAddCheckbox('mixFileKindBox', tr("Can mix file kind"))
        self.widgetsVLayout.addWidget(self.mixFileKindBox)
        self._setupAddCheckbox('useRegexpBox', tr("Use regular expressions when filtering"))
        self.widgetsVLayout.addWidget(self.useRegexpBox)
        self._setupAddCheckbox('removeEmptyFoldersBox', tr("Remove empty folders on delete or move"))
        self.widgetsVLayout.addWidget(self.removeEmptyFoldersBox)
        self._setupAddCheckbox('ignoreHardlinkMatches', tr("Ignore duplicates hardlinking to the same file"))
        self.widgetsVLayout.addWidget(self.ignoreHardlinkMatches)
        self._setupAddCheckbox('debugModeBox', tr(tr("Debug mode (restart required)")))
        self.widgetsVLayout.addWidget(self.debugModeBox)
        self._setupBottomPart()
    
    def _load(self, prefs, setchecked):
        scan_type_index = SCAN_TYPE_ORDER.index(prefs.scan_type)
        self.scanTypeComboBox.setCurrentIndex(scan_type_index)
        setchecked(self.tagTrackBox, prefs.scan_tag_track)
        setchecked(self.tagArtistBox, prefs.scan_tag_artist)
        setchecked(self.tagAlbumBox, prefs.scan_tag_album)
        setchecked(self.tagTitleBox, prefs.scan_tag_title)
        setchecked(self.tagGenreBox, prefs.scan_tag_genre)
        setchecked(self.tagYearBox, prefs.scan_tag_year)
        setchecked(self.matchSimilarBox, prefs.match_similar)
        setchecked(self.wordWeightingBox, prefs.word_weighting)
    
    def _save(self, prefs, ischecked):
        prefs.scan_type = SCAN_TYPE_ORDER[self.scanTypeComboBox.currentIndex()]
        prefs.scan_tag_track = ischecked(self.tagTrackBox)
        prefs.scan_tag_artist = ischecked(self.tagArtistBox)
        prefs.scan_tag_album = ischecked(self.tagAlbumBox)
        prefs.scan_tag_title = ischecked(self.tagTitleBox)
        prefs.scan_tag_genre = ischecked(self.tagGenreBox)
        prefs.scan_tag_year = ischecked(self.tagYearBox)
        prefs.match_similar = ischecked(self.matchSimilarBox)
        prefs.word_weighting = ischecked(self.wordWeightingBox)
    
    def resetToDefaults(self):
        self.load(preferences.Preferences())
    
    #--- Events
    def scanTypeChanged(self, index):
        scan_type = SCAN_TYPE_ORDER[self.scanTypeComboBox.currentIndex()]
        word_based = scan_type in (ScanType.Filename, ScanType.Fields, ScanType.FieldsNoOrder,
            ScanType.Tag)
        tag_based = scan_type == ScanType.Tag
        self.filterHardnessSlider.setEnabled(word_based)
        self.matchSimilarBox.setEnabled(word_based)
        self.wordWeightingBox.setEnabled(word_based)
        self.tagTrackBox.setEnabled(tag_based)
        self.tagArtistBox.setEnabled(tag_based)
        self.tagAlbumBox.setEnabled(tag_based)
        self.tagTitleBox.setEnabled(tag_based)
        self.tagGenreBox.setEnabled(tag_based)
        self.tagYearBox.setEnabled(tag_based)
    

if __name__ == '__main__':
    from ..testapp import TestApp
    app = QApplication([])
    dgapp = TestApp()
    dialog = PreferencesDialog(None, dgapp)
    dialog.show()
    sys.exit(app.exec_())