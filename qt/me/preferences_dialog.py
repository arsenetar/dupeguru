# Copyright 2016 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QSpacerItem,
    QWidget,
)

from hscommon.trans import trget
from core.app import AppMode
from core.scanner import ScanType

from qt.preferences_dialog import PreferencesDialogBase

tr = trget("ui")


class PreferencesDialog(PreferencesDialogBase):
    def _setupPreferenceWidgets(self):
        self._setupFilterHardnessBox()
        self.widgetsVLayout.addLayout(self.filterHardnessHLayout)
        self.widget = QWidget(self)
        self.widget.setMinimumSize(QSize(0, 40))
        self.verticalLayout_4 = QVBoxLayout(self.widget)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.label_6 = QLabel(self.widget)
        self.label_6.setText(tr("Tags to scan:"))
        self.verticalLayout_4.addWidget(self.label_6)
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setSpacing(0)
        spacer_item = QSpacerItem(15, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacer_item)
        self._setupAddCheckbox("tagTrackBox", tr("Track"), self.widget)
        self.horizontalLayout_2.addWidget(self.tagTrackBox)
        self._setupAddCheckbox("tagArtistBox", tr("Artist"), self.widget)
        self.horizontalLayout_2.addWidget(self.tagArtistBox)
        self._setupAddCheckbox("tagAlbumBox", tr("Album"), self.widget)
        self.horizontalLayout_2.addWidget(self.tagAlbumBox)
        self._setupAddCheckbox("tagTitleBox", tr("Title"), self.widget)
        self.horizontalLayout_2.addWidget(self.tagTitleBox)
        self._setupAddCheckbox("tagGenreBox", tr("Genre"), self.widget)
        self.horizontalLayout_2.addWidget(self.tagGenreBox)
        self._setupAddCheckbox("tagYearBox", tr("Year"), self.widget)
        self.horizontalLayout_2.addWidget(self.tagYearBox)
        self.verticalLayout_4.addLayout(self.horizontalLayout_2)
        self.widgetsVLayout.addWidget(self.widget)
        self._setupAddCheckbox("wordWeightingBox", tr("Word weighting"))
        self.widgetsVLayout.addWidget(self.wordWeightingBox)
        self._setupAddCheckbox("matchSimilarBox", tr("Match similar words"))
        self.widgetsVLayout.addWidget(self.matchSimilarBox)
        self._setupAddCheckbox("mixFileKindBox", tr("Can mix file kind"))
        self.widgetsVLayout.addWidget(self.mixFileKindBox)
        self._setupAddCheckbox("useRegexpBox", tr("Use regular expressions when filtering"))
        self.widgetsVLayout.addWidget(self.useRegexpBox)
        self._setupAddCheckbox("removeEmptyFoldersBox", tr("Remove empty folders on delete or move"))
        self.widgetsVLayout.addWidget(self.removeEmptyFoldersBox)
        self._setupAddCheckbox(
            "ignoreHardlinkMatches",
            tr("Ignore duplicates hardlinking to the same file"),
        )
        self.widgetsVLayout.addWidget(self.ignoreHardlinkMatches)
        self._setupBottomPart()

    def _load(self, prefs, setchecked, section):
        setchecked(self.tagTrackBox, prefs.scan_tag_track)
        setchecked(self.tagArtistBox, prefs.scan_tag_artist)
        setchecked(self.tagAlbumBox, prefs.scan_tag_album)
        setchecked(self.tagTitleBox, prefs.scan_tag_title)
        setchecked(self.tagGenreBox, prefs.scan_tag_genre)
        setchecked(self.tagYearBox, prefs.scan_tag_year)
        setchecked(self.matchSimilarBox, prefs.match_similar)
        setchecked(self.wordWeightingBox, prefs.word_weighting)

        # Update UI state based on selected scan type
        scan_type = prefs.get_scan_type(AppMode.MUSIC)
        word_based = scan_type in (
            ScanType.FILENAME,
            ScanType.FIELDS,
            ScanType.FIELDSNOORDER,
            ScanType.TAG,
        )
        tag_based = scan_type == ScanType.TAG
        self.filterHardnessSlider.setEnabled(word_based)
        self.matchSimilarBox.setEnabled(word_based)
        self.wordWeightingBox.setEnabled(word_based)
        self.tagTrackBox.setEnabled(tag_based)
        self.tagArtistBox.setEnabled(tag_based)
        self.tagAlbumBox.setEnabled(tag_based)
        self.tagTitleBox.setEnabled(tag_based)
        self.tagGenreBox.setEnabled(tag_based)
        self.tagYearBox.setEnabled(tag_based)

    def _save(self, prefs, ischecked):
        prefs.scan_tag_track = ischecked(self.tagTrackBox)
        prefs.scan_tag_artist = ischecked(self.tagArtistBox)
        prefs.scan_tag_album = ischecked(self.tagAlbumBox)
        prefs.scan_tag_title = ischecked(self.tagTitleBox)
        prefs.scan_tag_genre = ischecked(self.tagGenreBox)
        prefs.scan_tag_year = ischecked(self.tagYearBox)
        prefs.match_similar = ischecked(self.matchSimilarBox)
        prefs.word_weighting = ischecked(self.wordWeightingBox)
