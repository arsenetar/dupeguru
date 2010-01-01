# Created By: Virgil Dupras
# Created On: 2006/09/14
# $Id$
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import os
import logging
import sqlite3 as sqlite

import hsutil.sqlite

from _cache import string_to_colors

def colors_to_string(colors):
    """Transform the 3 sized tuples 'colors' into a hex string.
    
    [(0,100,255)] --> 0064ff
    [(1,2,3),(4,5,6)] --> 010203040506
    """
    return ''.join(['%02x%02x%02x' % (r,g,b) for r,g,b in colors])

# This function is an important bottleneck of dupeGuru PE. It has been converted to Cython.
# def string_to_colors(s):
#     """Transform the string 's' in a list of 3 sized tuples.
#     """
#     result = []
#     for i in xrange(0, len(s), 6):
#         number = int(s[i:i+6], 16)
#         result.append((number >> 16, (number >> 8) & 0xff, number & 0xff))
#     return result

class Cache(object):
    """A class to cache picture blocks.
    """
    def __init__(self, db=':memory:', threaded=True):
        def create_tables():
            sql = "create table pictures(path TEXT, blocks TEXT)"
            self.con.execute(sql);
            sql = "create index idx_path on pictures (path)"
            self.con.execute(sql)
        
        self.dbname = db
        if threaded:
            self.con = hsutil.sqlite.ThreadedConn(db, True)
        else:
            self.con = sqlite.connect(db, isolation_level=None)
        try:
            self.con.execute("select * from pictures where 1=2")
        except sqlite.OperationalError: # new db
            create_tables()
        except sqlite.DatabaseError, e: # corrupted db
            logging.warning('Could not create picture cache because of an error: %s', str(e))
            self.con.close()
            os.remove(db)
            if threaded:
                self.con = hsutil.sqlite.ThreadedConn(db, True)
            else:
                self.con = sqlite.connect(db, isolation_level=None)
            create_tables()
    
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
            result = string_to_colors(result[0])
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
    
    def __setitem__(self, key, value):
        value = colors_to_string(value)
        if key in self:
            sql = "update pictures set blocks = ? where path = ?"
        else:
            sql = "insert into pictures(blocks,path) values(?,?)"
        try:
            self.con.execute(sql, [value, key])
        except sqlite.OperationalError:
            logging.warning('Picture cache could not set %r for key %r', value, key)
        except sqlite.DatabaseError, e:
            logging.warning('DatabaseError while setting %r for key %r: %s', value, key, str(e))
    
    def clear(self):
        sql = "delete from pictures"
        self.con.execute(sql)
    
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
        sql = "select rowid, blocks from pictures where rowid in (%s)" % ','.join(map(str, rowids))
        cur = self.con.execute(sql)
        return ((rowid, string_to_colors(blocks)) for rowid, blocks in cur)
    
