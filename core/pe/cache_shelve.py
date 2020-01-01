# Copyright 2016 Virgil Dupras
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

import os
import os.path as op
import shelve
import tempfile
from collections import namedtuple

from .cache import string_to_colors, colors_to_string


def wrap_path(path):
    return "path:{}".format(path)


def unwrap_path(key):
    return key[5:]


def wrap_id(path):
    return "id:{}".format(path)


def unwrap_id(key):
    return int(key[3:])


CacheRow = namedtuple("CacheRow", "id path blocks mtime")


class ShelveCache:
    """A class to cache picture blocks in a shelve backend.
    """

    def __init__(self, db=None, readonly=False):
        self.istmp = db is None
        if self.istmp:
            self.dtmp = tempfile.mkdtemp()
            self.ftmp = db = op.join(self.dtmp, "tmpdb")
        flag = "r" if readonly else "c"
        self.shelve = shelve.open(db, flag)
        self.maxid = self._compute_maxid()

    def __contains__(self, key):
        return wrap_path(key) in self.shelve

    def __delitem__(self, key):
        row = self.shelve[wrap_path(key)]
        del self.shelve[wrap_path(key)]
        del self.shelve[wrap_id(row.id)]

    def __getitem__(self, key):
        if isinstance(key, int):
            skey = self.shelve[wrap_id(key)]
        else:
            skey = wrap_path(key)
        return string_to_colors(self.shelve[skey].blocks)

    def __iter__(self):
        return (unwrap_path(k) for k in self.shelve if k.startswith("path:"))

    def __len__(self):
        return sum(1 for k in self.shelve if k.startswith("path:"))

    def __setitem__(self, path_str, blocks):
        blocks = colors_to_string(blocks)
        if op.exists(path_str):
            mtime = int(os.stat(path_str).st_mtime)
        else:
            mtime = 0
        if path_str in self:
            rowid = self.shelve[wrap_path(path_str)].id
        else:
            rowid = self._get_new_id()
        row = CacheRow(rowid, path_str, blocks, mtime)
        self.shelve[wrap_path(path_str)] = row
        self.shelve[wrap_id(rowid)] = wrap_path(path_str)

    def _compute_maxid(self):
        return max(
            (unwrap_id(k) for k in self.shelve if k.startswith("id:")), default=1
        )

    def _get_new_id(self):
        self.maxid += 1
        return self.maxid

    def clear(self):
        self.shelve.clear()

    def close(self):
        if self.shelve is not None:
            self.shelve.close()
            if self.istmp:
                os.remove(self.ftmp)
                os.rmdir(self.dtmp)
        self.shelve = None

    def filter(self, func):
        to_delete = [key for key in self if not func(key)]
        for key in to_delete:
            del self[key]

    def get_id(self, path):
        if path in self:
            return self.shelve[wrap_path(path)].id
        else:
            raise ValueError(path)

    def get_multiple(self, rowids):
        for rowid in rowids:
            try:
                skey = self.shelve[wrap_id(rowid)]
            except KeyError:
                continue
            yield (rowid, string_to_colors(self.shelve[skey].blocks))

    def purge_outdated(self):
        """Go through the cache and purge outdated records.

        A record is outdated if the picture doesn't exist or if its mtime is greater than the one in
        the db.
        """
        todelete = []
        for path in self:
            row = self.shelve[wrap_path(path)]
            if row.mtime and op.exists(path):
                picture_mtime = os.stat(path).st_mtime
                if int(picture_mtime) <= row.mtime:
                    # not outdated
                    continue
            todelete.append(path)
        for path in todelete:
            try:
                del self[path]
            except KeyError:
                # I have no idea why a KeyError sometimes happen, but it does, as we can see in
                # #402 and #439. I don't think it hurts to silently ignore the error, so that's
                # what we do
                pass
