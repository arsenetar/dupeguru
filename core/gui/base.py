# Created By: Virgil Dupras
# Created On: 2010-02-06
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from hscommon.notify import Listener


class DupeGuruGUIObject(Listener):
    def __init__(self, app):
        Listener.__init__(self, app)
        self.app = app

    def directories_changed(self):
        pass

    def dupes_selected(self):
        pass

    def marking_changed(self):
        pass

    def results_changed(self):
        pass

    def results_changed_but_keep_selection(self):
        pass
