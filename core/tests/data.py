# Created By: Virgil Dupras
# Created On: 2009-10-23
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

# data module for tests

from hscommon.util import format_size
from ..data import cmp_value, Column

COLUMNS = [
    Column('name', 'Filename'),
    Column('folder_path', 'Directory'),
    Column('size', 'Size (KB)'),
    Column('extension', 'Kind'),
]

METADATA_TO_READ = ['size']
DELTA_COLUMNS = {2,}

def GetDisplayInfo(dupe, group, delta):
    size = dupe.size
    m = group.get_match_of(dupe)
    if m and delta:
        r = group.ref
        size -= r.size
    return [
        dupe.name,
        str(dupe.folder_path),
        format_size(size, 0, 1, False),
        dupe.extension if hasattr(dupe, 'extension') else '---',
    ]

def GetDupeSortKey(dupe, get_group, key, delta):
    r = cmp_value(getattr(dupe, COLUMNS[key].attr))
    if delta and (key in DELTA_COLUMNS):
        r -= cmp_value(getattr(get_group().ref, COLUMNS[key].attr))
    return r

def GetGroupSortKey(group, key):
    return cmp_value(getattr(group.ref, COLUMNS[key].attr))