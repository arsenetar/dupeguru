# Unit Name: dupeguru_pe.data
# Created By: Virgil Dupras
# Created On: 2006/03/15
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

from hsutil.str import format_size
from dupeguru.data import format_path, format_timestamp, format_perc, format_dupe_count, cmp_value

def format_dimensions(dimensions):
    return '%d x %d' % (dimensions[0], dimensions[1])

COLUMNS = [
    {'attr':'name','display':'Filename'},
    {'attr':'path','display':'Directory'},
    {'attr':'size','display':'Size (KB)'},
    {'attr':'extension','display':'Kind'},
    {'attr':'dimensions','display':'Dimensions'},
    {'attr':'ctime','display':'Creation'},
    {'attr':'mtime','display':'Modification'},
    {'attr':'percentage','display':'Match %'},
    {'attr':'dupe_count','display':'Dupe Count'},
]

def GetDisplayInfo(dupe,group,delta=False):
    if (dupe is None) or (group is None):
        return ['---'] * len(COLUMNS)
    size = dupe.size
    ctime = dupe.ctime
    mtime = dupe.mtime
    m = group.get_match_of(dupe)
    if m:
        percentage = m.percentage
        dupe_count = 0
        if delta:
            r = group.ref
            size -= r.size
            ctime -= r.ctime
            mtime -= r.mtime
    else:
        percentage = group.percentage
        dupe_count = len(group.dupes)
    dupe_path = getattr(dupe, 'display_path', dupe.path)
    return [
        dupe.name,
        format_path(dupe_path),
        format_size(size, 0, 1, False),
        dupe.extension,
        format_dimensions(dupe.dimensions),
        format_timestamp(ctime, delta and m),
        format_timestamp(mtime, delta and m),
        format_perc(percentage),
        format_dupe_count(dupe_count)
    ]

def GetDupeSortKey(dupe, get_group, key, delta):
    if key == 7:
        m = get_group().get_match_of(dupe)
        return m.percentage
    if key == 8:
        return 0
    r = cmp_value(getattr(dupe, COLUMNS[key]['attr']))
    if delta and (key in (2, 5, 6)):
        r -= cmp_value(getattr(get_group().ref, COLUMNS[key]['attr']))
    return r

def GetGroupSortKey(group, key):
    if key == 7:
        return group.percentage
    if key == 8:
        return len(group)
    return cmp_value(getattr(group.ref, COLUMNS[key]['attr']))

