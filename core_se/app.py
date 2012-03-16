# Created On: 2011/09/20
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hscommon.util import format_size

from core.app import (DupeGuru as DupeGuruBase, format_timestamp, format_perc,
    format_words, format_dupe_count)
from core import prioritize
from . import __appname__
from .result_table import ResultTable

class DupeGuru(DupeGuruBase):
    NAME = __appname__
    METADATA_TO_READ = ['size', 'mtime']
    
    def _get_display_info(self, dupe, group, delta):
        size = dupe.size
        mtime = dupe.mtime
        m = group.get_match_of(dupe)
        if m:
            percentage = m.percentage
            dupe_count = 0
            if delta:
                r = group.ref
                size -= r.size
                mtime -= r.mtime
        else:
            percentage = group.percentage
            dupe_count = len(group.dupes)
        return {
            'name': dupe.name,
            'folder_path': str(dupe.folder_path),
            'size': format_size(size, 0, 1, False),
            'extension': dupe.extension,
            'mtime': format_timestamp(mtime, delta and m),
            'percentage': format_perc(percentage),
            'words': format_words(dupe.words) if hasattr(dupe, 'words') else '',
            'dupe_count': format_dupe_count(dupe_count),
        }
    
    def _prioritization_categories(self):
        return prioritize.all_categories()
    
    def _create_result_table(self):
        return ResultTable(self)
    
