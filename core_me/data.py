# Created By: Virgil Dupras
# Created On: 2006/03/15
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from hsutil.str import format_time, FT_MINUTES, format_size
from core.data import (format_path, format_timestamp, format_words, format_perc, 
    format_dupe_count, cmp_value)

COLUMNS = [
    {'attr':'name','display':'Filename'},
    {'attr':'path','display':'Directory'},
    {'attr':'size','display':'Size (MB)'},
    {'attr':'duration','display':'Time'},
    {'attr':'bitrate','display':'Bitrate'},
    {'attr':'samplerate','display':'Sample Rate'},
    {'attr':'extension','display':'Kind'},
    {'attr':'mtime','display':'Modification'},
    {'attr':'title','display':'Title'},
    {'attr':'artist','display':'Artist'},
    {'attr':'album','display':'Album'},
    {'attr':'genre','display':'Genre'},
    {'attr':'year','display':'Year'},
    {'attr':'track','display':'Track Number'},
    {'attr':'comment','display':'Comment'},
    {'attr':'percentage','display':'Match %'},
    {'attr':'words','display':'Words Used'},
    {'attr':'dupe_count','display':'Dupe Count'},
]

METADATA_TO_READ = ['size', 'mtime', 'duration', 'bitrate', 'samplerate', 'title', 'artist',
    'album', 'genre', 'year', 'track', 'comment']

def GetDisplayInfo(dupe, group, delta):
    size = dupe.size
    duration = dupe.duration
    bitrate = dupe.bitrate
    samplerate = dupe.samplerate
    mtime = dupe.mtime
    m = group.get_match_of(dupe)
    if m:
        percentage = m.percentage
        dupe_count = 0
        if delta:
            r = group.ref
            size -= r.size
            duration -= r.duration
            bitrate -= r.bitrate
            samplerate -= r.samplerate
            mtime -= r.mtime
    else:
        percentage = group.percentage
        dupe_count = len(group.dupes)
    return [
        dupe.name,
        format_path(dupe.path),
        format_size(size, 2, 2, False),
        format_time(duration, FT_MINUTES),
        str(bitrate),
        str(samplerate),
        dupe.extension,
        format_timestamp(mtime,delta and m),
        dupe.title,
        dupe.artist,
        dupe.album,
        dupe.genre,
        dupe.year,
        str(dupe.track),
        dupe.comment,
        format_perc(percentage),
        format_words(dupe.words) if hasattr(dupe, 'words') else '',
        format_dupe_count(dupe_count)
    ]

def GetDupeSortKey(dupe, get_group, key, delta):
    if key == 16:
        m = get_group().get_match_of(dupe)
        return m.percentage
    if key == 18:
        return 0
    r = cmp_value(getattr(dupe, COLUMNS[key]['attr'], ''))
    if delta and (key in (2, 3, 4, 7, 8)):
        r -= cmp_value(getattr(get_group().ref, COLUMNS[key]['attr'], ''))
    return r

def GetGroupSortKey(group, key):
    if key == 16:
        return group.percentage
    if key == 18:
        return len(group)
    return cmp_value(getattr(group.ref, COLUMNS[key]['attr'], ''))
