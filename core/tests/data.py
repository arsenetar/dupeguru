# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-10-23
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

# data module for tests

from hsutil.str import format_size
from ..data import format_path, cmp_value

COLUMNS = [
    {'attr':'name','display':'Filename'},
    {'attr':'path','display':'Directory'},
    {'attr':'size','display':'Size (KB)'},
    {'attr':'extension','display':'Kind'},
]

METADATA_TO_READ = ['size']

def GetDisplayInfo(dupe, group, delta):
    size = dupe.size
    m = group.get_match_of(dupe)
    if m and delta:
        r = group.ref
        size -= r.size
    return [
        dupe.name,
        format_path(dupe.path),
        format_size(size, 0, 1, False),
        dupe.extension if hasattr(dupe, 'extension') else '---',
    ]

def GetDupeSortKey(dupe, get_group, key, delta):
    r = cmp_value(getattr(dupe, COLUMNS[key]['attr']))
    if delta and (key == 2):
        r -= cmp_value(getattr(get_group().ref, COLUMNS[key]['attr']))
    return r

def GetGroupSortKey(group, key):
    return cmp_value(getattr(group.ref, COLUMNS[key]['attr']))