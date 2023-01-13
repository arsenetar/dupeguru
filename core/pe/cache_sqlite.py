# Copyright 2016 Virgil Dupras
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

import os
import os.path as op
import logging
import sqlite3 as sqlite

from core.pe.cache import bytes_to_colors, colors_to_bytes


class SqliteCache:
    """A class to cache picture blocks in a sqlite backend."""

    schema_version = 1
    schema_version_description = "Changed from string to bytes for blocks."

    create_table_query = "CREATE TABLE IF NOT EXISTS pictures(path TEXT, mtime_ns INTEGER, blocks BLOB)"
    create_index_query = "CREATE INDEX IF NOT EXISTS idx_path on pictures (path)"
    drop_table_query = "DROP TABLE IF EXISTS pictures"
    drop_index_query = "DROP INDEX IF EXISTS idx_path"

    def __init__(self, db=":memory:", readonly=False):
        # readonly is not used in the sqlite version of the cache
        self.dbname = db
        self.con = None
        self._create_con()

    def __contains__(self, key):
        sql = "select count(*) from pictures where path = ?"
        result = self.con.execute(sql, [key]).fetchall()
        return result[0][0] > 0

    def __delitem__(self, key):
        if key not in self:
            raise KeyError(key)
        sql = "delete from pictures where path = ?"
        self.con.execute(sql, [key])

    # Optimized
    def __getitem__(self, key):
        if isinstance(key, int):
            sql = "select blocks from pictures where rowid = ?"
        else:
            sql = "select blocks from pictures where path = ?"
        result = self.con.execute(sql, [key]).fetchone()
        if result:
            result = bytes_to_colors(result[0])
            return result
        else:
            raise KeyError(key)

    def __iter__(self):
        sql = "select path from pictures"
        result = self.con.execute(sql)
        return (row[0] for row in result)

    def __len__(self):
        sql = "select count(*) from pictures"
        result = self.con.execute(sql).fetchall()
        return result[0][0]

    def __setitem__(self, path_str, blocks):
        blocks = colors_to_bytes(blocks)
        if op.exists(path_str):
            mtime = int(os.stat(path_str).st_mtime)
        else:
            mtime = 0
        if path_str in self:
            sql = "update pictures set blocks = ?, mtime_ns = ? where path = ?"
        else:
            sql = "insert into pictures(blocks,mtime_ns,path) values(?,?,?)"
        try:
            self.con.execute(sql, [blocks, mtime, path_str])
        except sqlite.OperationalError:
            logging.warning("Picture cache could not set value for key %r", path_str)
        except sqlite.DatabaseError as e:
            logging.warning("DatabaseError while setting value for key %r: %s", path_str, str(e))

    def _create_con(self, second_try=False):
        try:
            self.con = sqlite.connect(self.dbname, isolation_level=None)
            self._check_upgrade()
        except sqlite.DatabaseError as e:  # corrupted db
            if second_try:
                raise  # Something really strange is happening
            logging.warning("Could not create picture cache because of an error: %s", str(e))
            self.con.close()
            os.remove(self.dbname)
            self._create_con(second_try=True)

    def _check_upgrade(self) -> None:
        with self.con as conn:
            has_schema = conn.execute(
                "SELECT NAME FROM sqlite_master WHERE type='table' AND name='schema_version'"
            ).fetchall()
            version = None
            if has_schema:
                version = conn.execute("SELECT version FROM schema_version ORDER BY version DESC").fetchone()[0]
            else:
                conn.execute("CREATE TABLE schema_version (version int PRIMARY KEY, description TEXT)")
            if version != self.schema_version:
                conn.execute(self.drop_table_query)
                conn.execute(
                    "INSERT OR REPLACE INTO schema_version VALUES (:version, :description)",
                    {"version": self.schema_version, "description": self.schema_version_description},
                )
            conn.execute(self.create_table_query)
            conn.execute(self.create_index_query)

    def clear(self):
        self.close()
        if self.dbname != ":memory:":
            os.remove(self.dbname)
        self._create_con()

    def close(self):
        if self.con is not None:
            self.con.close()
        self.con = None

    def filter(self, func):
        to_delete = [key for key in self if not func(key)]
        for key in to_delete:
            del self[key]

    def get_id(self, path):
        sql = "select rowid from pictures where path = ?"
        result = self.con.execute(sql, [path]).fetchone()
        if result:
            return result[0]
        else:
            raise ValueError(path)

    def get_multiple(self, rowids):
        sql = "select rowid, blocks from pictures where rowid in (%s)" % ",".join(map(str, rowids))
        cur = self.con.execute(sql)
        return ((rowid, bytes_to_colors(blocks)) for rowid, blocks in cur)

    def purge_outdated(self):
        """Go through the cache and purge outdated records.

        A record is outdated if the picture doesn't exist or if its mtime is greater than the one in
        the db.
        """
        todelete = []
        sql = "select rowid, path, mtime_ns from pictures"
        cur = self.con.execute(sql)
        for rowid, path_str, mtime_ns in cur:
            if mtime_ns and op.exists(path_str):
                picture_mtime = os.stat(path_str).st_mtime
                if int(picture_mtime) <= mtime_ns:
                    # not outdated
                    continue
            todelete.append(rowid)
        if todelete:
            sql = "delete from pictures where rowid in (%s)" % ",".join(map(str, todelete))
            self.con.execute(sql)
