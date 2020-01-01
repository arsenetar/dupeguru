# Created By: Virgil Dupras
# Created On: 2013-07-14
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from hscommon.util import format_size

from core import fs
from core.util import format_timestamp, format_perc, format_words, format_dupe_count


def get_display_info(dupe, group, delta):
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
    return {
        "name": dupe.name,
        "folder_path": str(dupe.folder_path),
        "size": format_size(size, 0, 1, False),
        "extension": dupe.extension,
        "mtime": format_timestamp(mtime, delta and m),
        "percentage": format_perc(percentage),
        "words": format_words(dupe.words) if hasattr(dupe, "words") else "",
        "dupe_count": format_dupe_count(dupe_count),
    }


class File(fs.File):
    def get_display_info(self, group, delta):
        return get_display_info(self, group, delta)


class Folder(fs.Folder):
    def get_display_info(self, group, delta):
        return get_display_info(self, group, delta)
