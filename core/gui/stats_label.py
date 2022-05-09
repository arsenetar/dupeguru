# Created By: Virgil Dupras
# Created On: 2010-02-11
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from core.gui.base import DupeGuruGUIObject


class StatsLabel(DupeGuruGUIObject):
    def _view_updated(self):
        self.view.refresh()

    @property
    def display(self):
        return self.app.stat_line

    def results_changed(self):
        self.view.refresh()

    marking_changed = results_changed
