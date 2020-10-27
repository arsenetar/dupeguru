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
    QLineEdit,
)

from hscommon.trans import trget
from hscommon.util import tryint

from core.app import AppMode
from core.scanner import ScanType

from ..preferences_dialog import PreferencesDialogBase

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
        self._setupAddCheckbox(
            "matchSimilarBox", tr("Match similar words"), self.widget
        )
        self.verticalLayout_4.addWidget(self.matchSimilarBox)
        self._setupAddCheckbox("mixFileKindBox", tr("Can mix file kind"), self.widget)
        self.verticalLayout_4.addWidget(self.mixFileKindBox)
        self._setupAddCheckbox(
            "useRegexpBox", tr("Use regular expressions when filtering"), self.widget
        )
        self.verticalLayout_4.addWidget(self.useRegexpBox)
        self._setupAddCheckbox(
            "removeEmptyFoldersBox",
            tr("Remove empty folders on delete or move"),
            self.widget,
        )
        self.verticalLayout_4.addWidget(self.removeEmptyFoldersBox)
        self.horizontalLayout_2 = QHBoxLayout()
        self._setupAddCheckbox(
            "ignoreSmallFilesBox", tr("Ignore files smaller than"), self.widget
        )
        self.horizontalLayout_2.addWidget(self.ignoreSmallFilesBox)
        self.sizeThresholdEdit = QLineEdit(self.widget)
        sizePolicy = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.sizeThresholdEdit.sizePolicy().hasHeightForWidth()
        )
        self.sizeThresholdEdit.setSizePolicy(sizePolicy)
        self.sizeThresholdEdit.setMaximumSize(QSize(50, 16777215))
        self.horizontalLayout_2.addWidget(self.sizeThresholdEdit)
        self.label_6 = QLabel(self.widget)
        self.label_6.setText(tr("KB"))
        self.horizontalLayout_2.addWidget(self.label_6)
        spacerItem1 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.verticalLayout_4.addLayout(self.horizontalLayout_2)
        self._setupAddCheckbox(
            "ignoreHardlinkMatches",
            tr("Ignore duplicates hardlinking to the same file"),
            self.widget,
        )
        self.verticalLayout_4.addWidget(self.ignoreHardlinkMatches)
        self._setupAddCheckbox(
            "debugModeBox", tr("Debug mode (restart required)"), self.widget
        )
        self.verticalLayout_4.addWidget(self.debugModeBox)
        self.widgetsVLayout.addWidget(self.widget)
        self._setupBottomPart()

    def _load(self, prefs, setchecked, section):
        setchecked(self.matchSimilarBox, prefs.match_similar)
        setchecked(self.wordWeightingBox, prefs.word_weighting)
        setchecked(self.ignoreSmallFilesBox, prefs.ignore_small_files)
        self.sizeThresholdEdit.setText(str(prefs.small_file_threshold))

        # Update UI state based on selected scan type
        scan_type = prefs.get_scan_type(AppMode.Standard)
        word_based = scan_type == ScanType.Filename
        self.filterHardnessSlider.setEnabled(word_based)
        self.matchSimilarBox.setEnabled(word_based)
        self.wordWeightingBox.setEnabled(word_based)

    def _save(self, prefs, ischecked):
        prefs.match_similar = ischecked(self.matchSimilarBox)
        prefs.word_weighting = ischecked(self.wordWeightingBox)
        prefs.ignore_small_files = ischecked(self.ignoreSmallFilesBox)
        prefs.small_file_threshold = tryint(self.sizeThresholdEdit.text())
