# Created By: Virgil Dupras
# Created On: 2010-02-12
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html


class StatsLabel:
    def __init__(self, model, view):
        self.view = view
        self.model = model
        self.model.view = self

    def refresh(self):
        self.view.setText(self.model.display)
