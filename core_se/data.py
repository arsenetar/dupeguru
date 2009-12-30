# Created By: Virgil Dupras
# Created On: 2006/03/15
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from hsutil.str import format_size
from core.data import (format_path, format_timestamp, format_words, format_perc, 
    format_dupe_count, cmp_value)

COLUMNS = [
    {'attr':'name','display':'Filename'},
    {'attr':'path','display':'Directory'},
    {'attr':'size','display':'Size (KB)'},
    {'attr':'extension','display':'Kind'},
    {'attr':'ctime','display':'Creation'},
    {'attr':'mtime','display':'Modification'},
    {'attr':'percentage','display':'Match %'},
    {'attr':'words','display':'Words Used'},
    {'attr':'dupe_count','display':'Dupe Count'},
]

METADATA_TO_READ = ['size', 'ctime', 'mtime']

def GetDisplayInfo(dupe, group, delta):
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
    return [
        dupe.name,
        format_path(dupe.path),
        format_size(size, 0, 1, False),
        dupe.extension,
        format_timestamp(ctime, delta and m),
        format_timestamp(mtime, delta and m),
        format_perc(percentage),
        format_words(dupe.words) if hasattr(dupe, 'words') else '',
        format_dupe_count(dupe_count)
    ]

def GetDupeSortKey(dupe, get_group, key, delta):
    if key == 6:
        m = get_group().get_match_of(dupe)
        return m.percentage
    if key == 8:
        return 0
    r = cmp_value(getattr(dupe, COLUMNS[key]['attr']))
    if delta and (key in (2, 4, 5)):
        r -= cmp_value(getattr(get_group().ref, COLUMNS[key]['attr']))
    return r

def GetGroupSortKey(group, key):
    if key == 6:
        return group.percentage
    if key == 8:
        return len(group)
    return cmp_value(getattr(group.ref, COLUMNS[key]['attr']))
