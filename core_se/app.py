# Copyright 2016 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from core.app import DupeGuru as DupeGuruBase, AppMode
from core import prioritize
import core_me.fs
import core_me.prioritize
import core_me.result_table
import core_me.scanner
from . import __appname__, fs, scanner
from .result_table import ResultTable

class DupeGuru(DupeGuruBase):
    NAME = __appname__

    def __init__(self, view):
        DupeGuruBase.__init__(self, view)
        self.folderclass = fs.Folder

    def _get_dupe_sort_key(self, dupe, get_group, key, delta):
        if self.app_mode == AppMode.Music:
            if key == 'folder_path':
                dupe_folder_path = getattr(dupe, 'display_folder_path', dupe.folder_path)
                return str(dupe_folder_path).lower()
        return DupeGuruBase._get_dupe_sort_key(self, dupe, get_group, key, delta)

    def _get_group_sort_key(self, group, key):
        if self.app_mode == AppMode.Music:
            if key == 'folder_path':
                dupe_folder_path = getattr(group.ref, 'display_folder_path', group.ref.folder_path)
                return str(dupe_folder_path).lower()
        return DupeGuruBase._get_group_sort_key(self, group, key)

    def _prioritization_categories(self):
        if self.app_mode == AppMode.Music:
            return prioritize.all_categories()
        else:
            return prioritize.all_categories()

    def _create_result_table(self):
        if self.app_mode == AppMode.Music:
            return core_me.result_table.ResultTable(self)
        else:
            return ResultTable(self)

    @property
    def fileclasses(self):
        if self.app_mode == AppMode.Music:
            return [core_me.fs.MusicFile]
        else:
            return [fs.File]

    @property
    def SCANNER_CLASS(self):
        if self.app_mode == AppMode.Music:
            return core_me.scanner.ScannerME
        else:
            return scanner.ScannerSE

    @property
    def METADATA_TO_READ(self):
        if self.app_mode == AppMode.Music:
            return [
                'size', 'mtime', 'duration', 'bitrate', 'samplerate', 'title', 'artist',
                'album', 'genre', 'year', 'track', 'comment'
            ]
        else:
            return ['size', 'mtime']

