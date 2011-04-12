# Created By: Virgil Dupras
# Created On: 2006/03/15
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hscommon.util import format_size
from hscommon.trans import tr as trbase
from core.data import format_path, format_timestamp, format_perc, format_dupe_count, cmp_value, Column

tr = lambda s: trbase(s, 'columns')

def format_dimensions(dimensions):
    return '%d x %d' % (dimensions[0], dimensions[1])

COLUMNS = [
    Column('name', tr("Filename")),
    Column('path', tr("Folder")),
    Column('size', tr("Size (KB)")),
    Column('extension', tr("Kind")),
    Column('dimensions', tr("Dimensions")),
    Column('mtime', tr("Modification")),
    Column('percentage', tr("Match %")),
    Column('dupe_count', tr("Dupe Count")),
]

MATCHPERC_COL = 6
DUPECOUNT_COL = 7
DELTA_COLUMNS = {2, 4, 5}

METADATA_TO_READ = ['size', 'mtime', 'dimensions']

def get_delta_dimensions(value, ref_value):
    return (value[0]-ref_value[0], value[1]-ref_value[1])

def GetDisplayInfo(dupe,group,delta=False):
    if (dupe is None) or (group is None):
        return ['---'] * len(COLUMNS)
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
    dupe_path = getattr(dupe, 'display_path', dupe.path)
    return [
        dupe.name,
        format_path(dupe_path),
        format_size(size, 0, 1, False),
        dupe.extension,
        format_dimensions(dimensions),
        format_timestamp(mtime, delta and m),
        format_perc(percentage),
        format_dupe_count(dupe_count)
    ]

def GetDupeSortKey(dupe, get_group, key, delta):
    if key == MATCHPERC_COL:
        m = get_group().get_match_of(dupe)
        return m.percentage
    if key == DUPECOUNT_COL:
        return 0
    r = cmp_value(getattr(dupe, COLUMNS[key].attr, ''))
    if delta and (key in DELTA_COLUMNS):
        ref_value = cmp_value(getattr(get_group().ref, COLUMNS[key].attr, ''))
        if key == 4: # dimensions
            r = get_delta_dimensions(r, ref_value)
        else:
            r -= ref_value
    return r

def GetGroupSortKey(group, key):
    if key == MATCHPERC_COL:
        return group.percentage
    if key == DUPECOUNT_COL:
        return len(group)
    return cmp_value(getattr(group.ref, COLUMNS[key].attr, ''))

