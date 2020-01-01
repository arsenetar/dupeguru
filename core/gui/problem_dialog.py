# Created By: Virgil Dupras
# Created On: 2010-04-12
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from hscommon import desktop

from .problem_table import ProblemTable


class ProblemDialog:
    def __init__(self, app):
        self.app = app
        self._selected_dupe = None
        self.problem_table = ProblemTable(self)

    def refresh(self):
        self._selected_dupe = None
        self.problem_table.refresh()

    def reveal_selected_dupe(self):
        if self._selected_dupe is not None:
            desktop.reveal_path(self._selected_dupe.path)

    def select_dupe(self, dupe):
        self._selected_dupe = dupe
