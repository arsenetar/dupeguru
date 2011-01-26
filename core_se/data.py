# Created By: Virgil Dupras
# Created On: 2006/03/15
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hscommon.util import format_size
from hscommon.trans import tr as trbase
from core.data import (format_path, format_timestamp, format_words, format_perc, 
    format_dupe_count, cmp_value)

tr = lambda s: trbase(s, 'columns')

COLUMNS = [
    {'attr':'name', 'display': tr("Filename")},
    {'attr':'path', 'display': tr("Folder")},
    {'attr':'size', 'display': tr("Size (KB)")},
    {'attr':'extension', 'display': tr("Kind")},
    {'attr':'mtime', 'display': tr("Modification")},
    {'attr':'percentage', 'display': tr("Match %")},
    {'attr':'words', 'display': tr("Words Used")},
    {'attr':'dupe_count', 'display': tr("Dupe Count")},
]

MATCHPERC_COL = 5
DUPECOUNT_COL = 7

METADATA_TO_READ = ['size', 'mtime']

def GetDisplayInfo(dupe, group, delta):
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
    return [
        dupe.name,
        format_path(dupe.path),
        format_size(size, 0, 1, False),
        dupe.extension,
        format_timestamp(mtime, delta and m),
        format_perc(percentage),
        format_words(dupe.words) if hasattr(dupe, 'words') else '',
        format_dupe_count(dupe_count)
    ]

def GetDupeSortKey(dupe, get_group, key, delta):
    if key == MATCHPERC_COL:
        m = get_group().get_match_of(dupe)
        return m.percentage
    if key == DUPECOUNT_COL:
        return 0
    r = cmp_value(getattr(dupe, COLUMNS[key]['attr'], ''))
    if delta and (key in {2, 4}):
        r -= cmp_value(getattr(get_group().ref, COLUMNS[key]['attr'], ''))
    return r

def GetGroupSortKey(group, key):
    if key == MATCHPERC_COL:
        return group.percentage
    if key == DUPECOUNT_COL:
        return len(group)
    return cmp_value(getattr(group.ref, COLUMNS[key]['attr'], ''))
