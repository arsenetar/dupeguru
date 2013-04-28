# Created On: 2011/09/20
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import os.path as op

from hscommon.util import format_size

from core.app import (DupeGuru as DupeGuruBase, format_timestamp, format_perc,
    format_dupe_count, cmp_value)
from .scanner import ScannerPE
from . import prioritize
from . import __appname__
from .result_table import ResultTable

def format_dimensions(dimensions):
    return '%d x %d' % (dimensions[0], dimensions[1])

def get_delta_dimensions(value, ref_value):
    return (value[0]-ref_value[0], value[1]-ref_value[1])

class DupeGuru(DupeGuruBase):
    NAME = __appname__
    METADATA_TO_READ = ['size', 'mtime', 'dimensions', 'exif_timestamp']
    
    def __init__(self, view, appdata):
        DupeGuruBase.__init__(self, view, appdata)
        self.scanner = ScannerPE()
        self.scanner.cache_path = op.join(self.appdata, 'cached_pictures.db')
    
    def _get_display_info(self, dupe, group, delta):
        size = dupe.size
        mtime = dupe.mtime
        dimensions = dupe.dimensions
        m = group.get_match_of(dupe)
        if m:
            percentage = m.percentage
            dupe_count = 0
            if delta:
                r = group.ref
                size -= r.size
                mtime -= r.mtime
                dimensions = get_delta_dimensions(dimensions, r.dimensions)
        else:
            percentage = group.percentage
            dupe_count = len(group.dupes)
        dupe_folder_path = getattr(dupe, 'display_folder_path', dupe.folder_path)
        return {
            'name': dupe.name,
            'folder_path': str(dupe_folder_path),
            'size': format_size(size, 0, 1, False),
            'extension': dupe.extension,
            'dimensions': format_dimensions(dimensions),
            'exif_timestamp': dupe.exif_timestamp,
            'mtime': format_timestamp(mtime, delta and m),
            'percentage': format_perc(percentage),
            'dupe_count': format_dupe_count(dupe_count),
        }
    
    def _get_dupe_sort_key(self, dupe, get_group, key, delta):
        if key == 'folder_path':
            dupe_folder_path = getattr(dupe, 'display_folder_path', dupe.folder_path)
            return str(dupe_folder_path).lower()
        if delta and key == 'dimensions':
            r = cmp_value(dupe, key)
            ref_value = cmp_value(get_group().ref, key)
            return get_delta_dimensions(r, ref_value)
        return DupeGuruBase._get_dupe_sort_key(self, dupe, get_group, key, delta)
    
    def _get_group_sort_key(self, group, key):
        if key == 'folder_path':
            dupe_folder_path = getattr(group.ref, 'display_folder_path', group.ref.folder_path)
            return str(dupe_folder_path).lower()
        return DupeGuruBase._get_group_sort_key(self, group, key)
    
    def _prioritization_categories(self):
        return prioritize.all_categories()
    
    def _create_result_table(self):
        return ResultTable(self)
