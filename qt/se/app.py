# Copyright 2016 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from core_se import __appname__
from core_se.app import DupeGuru as DupeGuruModel
from core.directories import Directories as DirectoriesBase, DirectoryState
from core.app import AppMode
import core_pe.photo

from ..base.app import DupeGuru as DupeGuruBase
from .details_dialog import DetailsDialog as DetailsDialogStandard
from ..me.details_dialog import DetailsDialog as DetailsDialogMusic
from ..pe.details_dialog import DetailsDialog as DetailsDialogPicture
from .results_model import ResultsModel as ResultsModelStandard
from ..me.results_model import ResultsModel as ResultsModelMusic
from ..pe.results_model import ResultsModel as ResultsModelPicture
from .preferences import Preferences
from .preferences_dialog import PreferencesDialog as PreferencesDialogStandard
from ..me.preferences_dialog import PreferencesDialog as PreferencesDialogMusic
from ..pe.preferences_dialog import PreferencesDialog as PreferencesDialogPicture
from ..pe.photo import File as PlatSpecificPhoto

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

    PREFERENCES_CLASS = Preferences

    def _setup(self):
        self.directories = Directories()
        DupeGuruBase._setup(self)
        core_pe.photo.PLAT_SPECIFIC_PHOTO_CLASS = PlatSpecificPhoto

    def _update_options(self):
        DupeGuruBase._update_options(self)
        self.model.options['min_match_percentage'] = self.prefs.filter_hardness
        self.model.options['word_weighting'] = self.prefs.word_weighting
        self.model.options['match_similar_words'] = self.prefs.match_similar
        threshold = self.prefs.small_file_threshold if self.prefs.ignore_small_files else 0
        self.model.options['size_threshold'] = threshold * 1024 # threshold is in KB. the scanner wants bytes
        scanned_tags = set()
        if self.prefs.scan_tag_track:
            scanned_tags.add('track')
        if self.prefs.scan_tag_artist:
            scanned_tags.add('artist')
        if self.prefs.scan_tag_album:
            scanned_tags.add('album')
        if self.prefs.scan_tag_title:
            scanned_tags.add('title')
        if self.prefs.scan_tag_genre:
            scanned_tags.add('genre')
        if self.prefs.scan_tag_year:
            scanned_tags.add('year')
        self.model.options['scanned_tags'] = scanned_tags
        self.model.options['match_scaled'] = self.prefs.match_scaled

    @property
    def DETAILS_DIALOG_CLASS(self):
        if self.model.app_mode == AppMode.Picture:
            return DetailsDialogPicture
        elif self.model.app_mode == AppMode.Music:
            return DetailsDialogMusic
        else:
            return DetailsDialogStandard

    @property
    def RESULT_MODEL_CLASS(self):
        if self.model.app_mode == AppMode.Picture:
            return ResultsModelPicture
        elif self.model.app_mode == AppMode.Music:
            return ResultsModelMusic
        else:
            return ResultsModelStandard

    @property
    def PREFERENCES_DIALOG_CLASS(self):
        if self.model.app_mode == AppMode.Picture:
            return PreferencesDialogPicture
        elif self.model.app_mode == AppMode.Music:
            return PreferencesDialogMusic
        else:
            return PreferencesDialogStandard

