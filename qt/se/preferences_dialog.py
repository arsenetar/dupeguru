# Copyright 2016 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import (
    QSpinBox,
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
        self.widget.setMinimumSize(QSize(0, 136))
        self.verticalLayout_4 = QVBoxLayout(self.widget)
        self._setupAddCheckbox("wordWeightingBox", tr("Word weighting"), self.widget)
        self.verticalLayout_4.addWidget(self.wordWeightingBox)
        self._setupAddCheckbox("matchSimilarBox", tr("Match similar words"), self.widget)
        self.verticalLayout_4.addWidget(self.matchSimilarBox)
        self._setupAddCheckbox("mixFileKindBox", tr("Can mix file kind"), self.widget)
        self.verticalLayout_4.addWidget(self.mixFileKindBox)
        self._setupAddCheckbox("useRegexpBox", tr("Use regular expressions when filtering"), self.widget)
        self.verticalLayout_4.addWidget(self.useRegexpBox)
        self._setupAddCheckbox(
            "removeEmptyFoldersBox",
            tr("Remove empty folders on delete or move"),
            self.widget,
        )
        self.verticalLayout_4.addWidget(self.removeEmptyFoldersBox)
        self.horizontalLayout_2 = QHBoxLayout()
        self._setupAddCheckbox("ignoreSmallFilesBox", tr("Ignore files smaller than"), self.widget)
        self.horizontalLayout_2.addWidget(self.ignoreSmallFilesBox)
        self.sizeThresholdSpinBox = QSpinBox(self.widget)
        size_policy = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.sizeThresholdSpinBox.sizePolicy().hasHeightForWidth())
        self.sizeThresholdSpinBox.setSizePolicy(size_policy)
        self.sizeThresholdSpinBox.setMaximumSize(QSize(300, 16777215))
        self.sizeThresholdSpinBox.setRange(0, 1000000)
        self.horizontalLayout_2.addWidget(self.sizeThresholdSpinBox)
        self.label_6 = QLabel(self.widget)
        self.label_6.setText(tr("KB"))
        self.horizontalLayout_2.addWidget(self.label_6)
        spacer_item1 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacer_item1)
        self.verticalLayout_4.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_2a = QHBoxLayout()
        self._setupAddCheckbox("ignoreLargeFilesBox", tr("Ignore files larger than"), self.widget)
        self.horizontalLayout_2a.addWidget(self.ignoreLargeFilesBox)
        self.sizeSaturationSpinBox = QSpinBox(self.widget)
        size_policy = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        self.sizeSaturationSpinBox.setSizePolicy(size_policy)
        self.sizeSaturationSpinBox.setMaximumSize(QSize(300, 16777215))
        self.sizeSaturationSpinBox.setRange(0, 1000000)
        self.horizontalLayout_2a.addWidget(self.sizeSaturationSpinBox)
        self.label_6a = QLabel(self.widget)
        self.label_6a.setText(tr("MB"))
        self.horizontalLayout_2a.addWidget(self.label_6a)
        spacer_item3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_2a.addItem(spacer_item3)
        self.verticalLayout_4.addLayout(self.horizontalLayout_2a)
        self.horizontalLayout_2b = QHBoxLayout()
        self._setupAddCheckbox(
            "bigFilePartialHashesBox",
            tr("Partially hash files bigger than"),
            self.widget,
        )
        self.horizontalLayout_2b.addWidget(self.bigFilePartialHashesBox)
        self.bigSizeThresholdSpinBox = QSpinBox(self.widget)
        self.bigSizeThresholdSpinBox.setSizePolicy(size_policy)
        self.bigSizeThresholdSpinBox.setMaximumSize(QSize(300, 16777215))
        self.bigSizeThresholdSpinBox.setRange(0, 1000000)
        self.horizontalLayout_2b.addWidget(self.bigSizeThresholdSpinBox)
        self.label_6b = QLabel(self.widget)
        self.label_6b.setText(tr("MB"))
        self.horizontalLayout_2b.addWidget(self.label_6b)
        spacer_item2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_2b.addItem(spacer_item2)
        self.verticalLayout_4.addLayout(self.horizontalLayout_2b)
        self._setupAddCheckbox(
            "ignoreHardlinkMatches",
            tr("Ignore duplicates hardlinking to the same file"),
            self.widget,
        )
        self.verticalLayout_4.addWidget(self.ignoreHardlinkMatches)
        self.widgetsVLayout.addWidget(self.widget)
        self._setupBottomPart()

    def _load(self, prefs, setchecked, section):
        setchecked(self.matchSimilarBox, prefs.match_similar)
        setchecked(self.wordWeightingBox, prefs.word_weighting)
        setchecked(self.ignoreSmallFilesBox, prefs.ignore_small_files)
        self.sizeThresholdSpinBox.setValue(prefs.small_file_threshold)
        setchecked(self.ignoreLargeFilesBox, prefs.ignore_large_files)
        self.sizeSaturationSpinBox.setValue(prefs.large_file_threshold)
        setchecked(self.bigFilePartialHashesBox, prefs.big_file_partial_hashes)
        self.bigSizeThresholdSpinBox.setValue(prefs.big_file_size_threshold)

        # Update UI state based on selected scan type
        scan_type = prefs.get_scan_type(AppMode.STANDARD)
        word_based = scan_type == ScanType.FILENAME
        self.filterHardnessSlider.setEnabled(word_based)
        self.matchSimilarBox.setEnabled(word_based)
        self.wordWeightingBox.setEnabled(word_based)

    def _save(self, prefs, ischecked):
        prefs.match_similar = ischecked(self.matchSimilarBox)
        prefs.word_weighting = ischecked(self.wordWeightingBox)
        prefs.ignore_small_files = ischecked(self.ignoreSmallFilesBox)
        prefs.small_file_threshold = self.sizeThresholdSpinBox.value()
        prefs.ignore_large_files = ischecked(self.ignoreLargeFilesBox)
        prefs.large_file_threshold = self.sizeSaturationSpinBox.value()
        prefs.big_file_partial_hashes = ischecked(self.bigFilePartialHashesBox)
        prefs.big_file_size_threshold = self.bigSizeThresholdSpinBox.value()
