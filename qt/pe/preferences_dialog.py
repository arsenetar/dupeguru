# Created By: Virgil Dupras
# Created On: 2009-04-29
# Copyright 2014 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import sys
from PyQt5.QtWidgets import QApplication

from hscommon.trans import trget
from core.scanner import ScanType

from ..base.preferences_dialog import PreferencesDialogBase
from . import preferences

tr = trget('ui')

SCAN_TYPE_ORDER = [
    ScanType.FuzzyBlock,
    ScanType.ExifTimestamp,
]

class PreferencesDialog(PreferencesDialogBase):
    def __init__(self, parent, app):
        PreferencesDialogBase.__init__(self, parent, app)
        
        self.scanTypeComboBox.currentIndexChanged[int].connect(self.scanTypeChanged)
    
    def _setupPreferenceWidgets(self):
        scanTypeLabels = [
            tr("Contents"),
            tr("EXIF Timestamp"),
        ]
        self._setupScanTypeBox(scanTypeLabels)
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
        scan_type_index = SCAN_TYPE_ORDER.index(prefs.scan_type)
        self.scanTypeComboBox.setCurrentIndex(scan_type_index)
        setchecked(self.matchScaledBox, prefs.match_scaled)
    
    def _save(self, prefs, ischecked):
        prefs.scan_type = SCAN_TYPE_ORDER[self.scanTypeComboBox.currentIndex()]
        prefs.match_scaled = ischecked(self.matchScaledBox)
    
    def resetToDefaults(self):
        self.load(preferences.Preferences())
    
    #--- Events
    def scanTypeChanged(self, index):
        scan_type = SCAN_TYPE_ORDER[self.scanTypeComboBox.currentIndex()]
        fuzzy_scan = scan_type == ScanType.FuzzyBlock
        self.filterHardnessSlider.setEnabled(fuzzy_scan)
    

if __name__ == '__main__':
    from ..testapp import TestApp
    app = QApplication([])
    dgapp = TestApp()
    dialog = PreferencesDialog(None, dgapp)
    dialog.show()
    sys.exit(app.exec_())