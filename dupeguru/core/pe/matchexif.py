# Created By: Virgil Dupras
# Created On: 2011-04-20
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from collections import defaultdict
from itertools import combinations

from hscommon.trans import tr

from core.engine import Match


def getmatches(files, match_scaled, j):
    timestamp2pic = defaultdict(set)
    for picture in j.iter_with_progress(files, tr("Read EXIF of %d/%d pictures")):
        timestamp = picture.exif_timestamp
        if timestamp:
            timestamp2pic[timestamp].add(picture)
    if "0000:00:00 00:00:00" in timestamp2pic:  # very likely false matches
        del timestamp2pic["0000:00:00 00:00:00"]
    matches = []
    for pictures in timestamp2pic.values():
        for p1, p2 in combinations(pictures, 2):
            if (not match_scaled) and (p1.dimensions != p2.dimensions):
                continue
            matches.append(Match(p1, p2, 100))
    return matches
