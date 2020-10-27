# Copyright 2016 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from PyQt5.QtWidgets import QFormLayout
from PyQt5.QtCore import Qt
from hscommon.trans import trget
from hscommon.plat import ISLINUX
from qtlib.radio_box import RadioBox
from core.scanner import ScanType
from core.app import AppMode

from ..preferences_dialog import PreferencesDialogBase

tr = trget("ui")


class PreferencesDialog(PreferencesDialogBase):
    def _setupPreferenceWidgets(self):
        self._setupFilterHardnessBox()
        self.widgetsVLayout.addLayout(self.filterHardnessHLayout)
        self._setupAddCheckbox(
            "matchScaledBox", tr("Match pictures of different dimensions")
        )
        self.widgetsVLayout.addWidget(self.matchScaledBox)
        self._setupAddCheckbox("mixFileKindBox", tr("Can mix file kind"))
        self.widgetsVLayout.addWidget(self.mixFileKindBox)
        self._setupAddCheckbox(
            "useRegexpBox", tr("Use regular expressions when filtering")
        )
        self.widgetsVLayout.addWidget(self.useRegexpBox)
        self._setupAddCheckbox(
            "removeEmptyFoldersBox", tr("Remove empty folders on delete or move")
        )
        self.widgetsVLayout.addWidget(self.removeEmptyFoldersBox)
        self._setupAddCheckbox(
            "ignoreHardlinkMatches",
            tr("Ignore duplicates hardlinking to the same file"),
        )
        self.widgetsVLayout.addWidget(self.ignoreHardlinkMatches)
        self._setupAddCheckbox("debugModeBox", tr("Debug mode (restart required)"))
        self.widgetsVLayout.addWidget(self.debugModeBox)

        self.cacheTypeRadio = RadioBox(self, items=["Sqlite", "Shelve"], spread=False)
        cache_form = QFormLayout()
        cache_form.setLabelAlignment(Qt.AlignLeft)
        cache_form.addRow(tr("Picture cache mode:"), self.cacheTypeRadio)
        self.widgetsVLayout.addLayout(cache_form)
        self._setupBottomPart()

    def _setupDisplayPage(self):
        super()._setupDisplayPage()
        self._setupAddCheckbox("details_dialog_override_theme_icons",
                               tr("Override theme icons in viewer toolbar"))
        self.details_dialog_override_theme_icons.setToolTip(
            tr("Use our own internal icons instead of those provided by the theme engine"))
        # Prevent changing this on platforms where themes are unpredictable
        self.details_dialog_override_theme_icons.setEnabled(False if not ISLINUX else True)
        # Insert this right after the vertical title bar option
        index = self.details_groupbox_layout.indexOf(self.details_dialog_vertical_titlebar)
        self.details_groupbox_layout.insertWidget(
            index + 1, self.details_dialog_override_theme_icons)
        self._setupAddCheckbox("details_dialog_viewers_show_scrollbars",
                               tr("Show scrollbars in image viewers"))
        self.details_dialog_viewers_show_scrollbars.setToolTip(
            tr("When the image displayed doesn't fit the viewport, \
show scrollbars to span the view around"))
        self.details_groupbox_layout.insertWidget(
            index + 2, self.details_dialog_viewers_show_scrollbars)

    def _load(self, prefs, setchecked, section):
        setchecked(self.matchScaledBox, prefs.match_scaled)
        self.cacheTypeRadio.selected_index = (
            1 if prefs.picture_cache_type == "shelve" else 0
        )

        # Update UI state based on selected scan type
        scan_type = prefs.get_scan_type(AppMode.Picture)
        fuzzy_scan = scan_type == ScanType.FuzzyBlock
        self.filterHardnessSlider.setEnabled(fuzzy_scan)
        setchecked(self.details_dialog_override_theme_icons,
                   prefs.details_dialog_override_theme_icons)
        setchecked(self.details_dialog_viewers_show_scrollbars,
                   prefs.details_dialog_viewers_show_scrollbars)

    def _save(self, prefs, ischecked):
        prefs.match_scaled = ischecked(self.matchScaledBox)
        prefs.picture_cache_type = (
            "shelve" if self.cacheTypeRadio.selected_index == 1 else "sqlite"
        )
        prefs.details_dialog_override_theme_icons =\
            ischecked(self.details_dialog_override_theme_icons)
        prefs.details_dialog_viewers_show_scrollbars =\
            ischecked(self.details_dialog_viewers_show_scrollbars)
