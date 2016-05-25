# Copyright 2016 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from hscommon.trans import trget
from core.scanner import ScanType

from ..base.preferences_dialog import PreferencesDialogBase
from . import preferences

tr = trget('ui')

class PreferencesDialog(PreferencesDialogBase):
    def __init__(self, parent, app):
        PreferencesDialogBase.__init__(self, parent, app)

        self.scanTypeComboBox.currentIndexChanged[int].connect(self.scanTypeChanged)

    def _setupPreferenceWidgets(self):
        self._setupScanTypeBox()
        self._setupFilterHardnessBox()
        self.widgetsVLayout.addLayout(self.filterHardnessHLayout)
        self._setupAddCheckbox('matchScaledBox', tr("Match pictures of different dimensions"))
        self.widgetsVLayout.addWidget(self.matchScaledBox)
        self._setupAddCheckbox('mixFileKindBox', tr("Can mix file kind"))
        self.widgetsVLayout.addWidget(self.mixFileKindBox)
        self._setupAddCheckbox('useRegexpBox', tr("Use regular expressions when filtering"))
        self.widgetsVLayout.addWidget(self.useRegexpBox)
        self._setupAddCheckbox('removeEmptyFoldersBox', tr("Remove empty folders on delete or move"))
        self.widgetsVLayout.addWidget(self.removeEmptyFoldersBox)
        self._setupAddCheckbox('ignoreHardlinkMatches', tr("Ignore duplicates hardlinking to the same file"))
        self.widgetsVLayout.addWidget(self.ignoreHardlinkMatches)
        self._setupAddCheckbox('debugModeBox', tr("Debug mode (restart required)"))
        self.widgetsVLayout.addWidget(self.debugModeBox)
        self._setupBottomPart()

    def _load(self, prefs, setchecked):
        self._load_scan_type(prefs)
        setchecked(self.matchScaledBox, prefs.match_scaled)

    def _save(self, prefs, ischecked):
        self._save_scan_type(prefs)
        prefs.match_scaled = ischecked(self.matchScaledBox)

    def resetToDefaults(self):
        self.load(preferences.Preferences())

    #--- Events
    def scanTypeChanged(self, index):
        scan_options = self.app.model.scanner.get_scan_options()
        scan_type = scan_options[self.scanTypeComboBox.currentIndex()].scan_type
        fuzzy_scan = scan_type == ScanType.FuzzyBlock
        self.filterHardnessSlider.setEnabled(fuzzy_scan)

