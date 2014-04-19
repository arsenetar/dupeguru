# Created On: 2011/09/20
# Copyright 2014 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from core.app import DupeGuru as DupeGuruBase
from core import prioritize
from . import __appname__, fs
from .result_table import ResultTable

class DupeGuru(DupeGuruBase):
    NAME = __appname__
    METADATA_TO_READ = ['size', 'mtime']
    
    def __init__(self, view):
        DupeGuruBase.__init__(self, view)
        self.directories.fileclasses = [fs.File]
        self.directories.folderclass = fs.Folder
    
    def _prioritization_categories(self):
        return prioritize.all_categories()
    
    def _create_result_table(self):
        return ResultTable(self)
    
