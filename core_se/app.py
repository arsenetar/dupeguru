# Copyright 2016 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from core.app import DupeGuru as DupeGuruBase
from core import prioritize
from . import __appname__, fs, scanner
from .result_table import ResultTable

class DupeGuru(DupeGuruBase):
    NAME = __appname__
    METADATA_TO_READ = ['size', 'mtime']
    SCANNER_CLASS = scanner.ScannerSE

    def __init__(self, view):
        DupeGuruBase.__init__(self, view)
        self.fileclasses = [fs.File]
        self.folderclass = fs.Folder

    def _prioritization_categories(self):
        return prioritize.all_categories()

    def _create_result_table(self):
        return ResultTable(self)

