# Created By: Virgil Dupras
# Created On: 2009-04-29
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import sys
from PyQt4.QtGui import QLabel, QApplication

from hscommon.trans import tr

from ..base.preferences_dialog import PreferencesDialogBase
from . import preferences

class PreferencesDialog(PreferencesDialogBase):
    def _setupPreferenceWidgets(self):
        self._setupFilterHardnessBox()
        self.widgetsVLayout.addLayout(self.filterHardnessHLayout)
        self._setupAddCheckbox('matchScaledBox', tr("Match scaled pictures together"))
        self.widgetsVLayout.addWidget(self.matchScaledBox)
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
        setchecked(self.matchScaledBox, prefs.match_scaled)
    
    def _save(self, prefs, ischecked):
        prefs.match_scaled = ischecked(self.matchScaledBox)
    
    def resetToDefaults(self):
        self.load(preferences.Preferences())
    

if __name__ == '__main__':
    from ..testapp import TestApp
    app = QApplication([])
    dgapp = TestApp()
    dialog = PreferencesDialog(None, dgapp)
    dialog.show()
    sys.exit(app.exec_())