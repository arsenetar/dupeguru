# Created By: Virgil Dupras
# Created On: 2013-07-14
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hscommon.util import format_size

from core import fs
from core.app import format_timestamp, format_perc, format_words, format_dupe_count

class File(fs.File):
    def get_display_info(self, group, delta):
        size = self.size
        mtime = self.mtime
        m = group.get_match_of(self)
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
            'name': self.name,
            'folder_path': str(self.folder_path),
            'size': format_size(size, 0, 1, False),
            'extension': self.extension,
            'mtime': format_timestamp(mtime, delta and m),
            'percentage': format_perc(percentage),
            'words': format_words(self.words) if hasattr(self, 'words') else '',
            'dupe_count': format_dupe_count(dupe_count),
        }
    
