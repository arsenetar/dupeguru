# Created By: Virgil Dupras
# Created On: 2011-04-20
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from collections import defaultdict
from itertools import combinations

from hscommon.trans import tr
from jobprogress import job

from core.engine import Match

def group_by_timestamp(files, date_only=False, j=job.nulljob):
    """Returns a mapping timestamp --> set(files).

    If ``date_only`` is ``True``, ignore the "time" part of the timestamp and consider files as
    matching as soon as their date part match.
    """
    timestamp2pic = defaultdict(set)
    for picture in j.iter_with_progress(files, tr("Read EXIF of %d/%d pictures")):
        timestamp = picture.exif_timestamp
        if timestamp:
            if date_only:
                timestamp = timestamp[:10]
            timestamp2pic[timestamp].add(picture)
    NULL_TS = '0000:00:00 00:00:00'
    if date_only:
        NULL_TS = NULL_TS[:10]
    if NULL_TS in timestamp2pic: # very likely false matches
        del timestamp2pic[NULL_TS]
    return timestamp2pic

def getmatches(files, match_scaled=True, date_only=False, j=job.nulljob):
    """Returns a list of files with the same EXIF date.

    Reads the EXIF tag of all ``files`` and return a :class:`Match` for every pair of files having
    the exact same EXIF timestamp (DateTimeOriginal).

    If ``match_scaled`` if ``False``, ignore files that don't have the same dimensions.
    """
    timestamp2pic = group_by_timestamp(files, j=j)
    matches = []
    for pictures in timestamp2pic.values():
        for p1, p2 in combinations(pictures, 2):
            if (not match_scaled) and (p1.dimensions != p2.dimensions):
                continue
            matches.append(Match(p1, p2, 100))
    return matches
