# Created By: Virgil Dupras
# Created On: 2009-05-24
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "BSD" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.hardcoded.net/licenses/bsd_license

from core_se import __appname__
from core_se.app import DupeGuru as DupeGuruModel
from core.directories import Directories as DirectoriesBase, DirectoryState

from ..base.app import DupeGuru as DupeGuruBase
from .details_dialog import DetailsDialog
from .results_model import ResultsModel
from .preferences import Preferences
from .preferences_dialog import PreferencesDialog

class Directories(DirectoriesBase):
    ROOT_PATH_TO_EXCLUDE = frozenset(['windows', 'program files'])

    def _default_state_for_path(self, path):
        result = DirectoriesBase._default_state_for_path(self, path)
        if result is not None:
            return result
        if len(path) == 2 and path[1].lower() in self.ROOT_PATH_TO_EXCLUDE:
            return DirectoryState.Excluded

class DupeGuru(DupeGuruBase):
    MODELCLASS = DupeGuruModel
    EDITION = 'se'
    LOGO_NAME = 'logo_se'
    NAME = __appname__

    DETAILS_DIALOG_CLASS = DetailsDialog
    RESULT_MODEL_CLASS = ResultsModel
    PREFERENCES_CLASS = Preferences
    PREFERENCES_DIALOG_CLASS = PreferencesDialog

    def _setup(self):
        self.directories = Directories()
        DupeGuruBase._setup(self)

    def _update_options(self):
        DupeGuruBase._update_options(self)
        self.model.scanner.min_match_percentage = self.prefs.filter_hardness
        self.model.scanner.scan_type = self.prefs.scan_type
        self.model.scanner.word_weighting = self.prefs.word_weighting
        self.model.scanner.match_similar_words = self.prefs.match_similar
        threshold = self.prefs.small_file_threshold if self.prefs.ignore_small_files else 0
        self.model.scanner.size_threshold = threshold * 1024 # threshold is in KB. the scanner wants bytes

