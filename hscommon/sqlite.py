# Created By: Virgil Dupras
# Created On: 2007/05/19
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.gnu.org/licenses/gpl-3.0.html

import sys
import os
import os.path as op
import threading
from queue import Queue
import time
import sqlite3 as sqlite

STOP = object()
COMMIT = object()
ROLLBACK = object()

class FakeCursor(list):
    # It's not possible to use sqlite cursors on another thread than the connection. Thus,
    # we can't directly return the cursor. We have to fatch all results, and support its interface.
    def fetchall(self):
        return self
    
    def fetchone(self):
        try:
            return self.pop(0)
        except IndexError:
            return None
    

class _ActualThread(threading.Thread):
    ''' We can't use this class directly because thread object are not automatically freed when
        nothing refers to it, making it hang the application if not explicitely closed.
    '''
    def __init__(self, dbname, autocommit):
        threading.Thread.__init__(self)
        self._queries = Queue()
        self._results = Queue()
        self._dbname = dbname
        self._autocommit = autocommit
        self._waiting_list = set()
        self._lock = threading.Lock()
        self._run = True
        self.lastrowid = -1
        self.setDaemon(True)
        self.start()
    
    def _query(self, query):
        with self._lock:
            wait_token = object()
            self._waiting_list.add(wait_token)
            self._queries.put(query)
            self._waiting_list.remove(wait_token)
            result = self._results.get()
        return result
    
    def close(self):
        if not self._run:
            return
        self._query(STOP)
    
    def commit(self):
        if not self._run:
            return None # Connection closed
        self._query(COMMIT)
    
    def execute(self, sql, values=()):
        if not self._run:
            return None # Connection closed
        result = self._query((sql, values))
        if isinstance(result, Exception):
            raise result
        return result
    
    def rollback(self):
        if not self._run:
            return None # Connection closed
        self._query(ROLLBACK)
    
    def run(self):
        # The whole chdir thing is because sqlite doesn't handle directory names with non-asci char in the AT ALL.
        oldpath = os.getcwd()
        dbdir, dbname = op.split(self._dbname)
        if dbdir:
            os.chdir(dbdir)
        if self._autocommit:
            con = sqlite.connect(dbname, isolation_level=None)
        else:
            con = sqlite.connect(dbname)
        os.chdir(oldpath)
        while self._run or self._waiting_list:
            query = self._queries.get()
            result = None
            if query is STOP:
                self._run = False
            elif query is COMMIT:
                con.commit()
            elif query is ROLLBACK:
                con.rollback()
            else:
                sql, values = query
                try:
                    cur = con.execute(sql, values)
                    self.lastrowid = cur.lastrowid
                    result = FakeCursor(cur.fetchall())
                    result.lastrowid = cur.lastrowid
                except Exception as e:
                    result = e
            self._results.put(result)
        con.close()
    

class ThreadedConn:
    """``sqlite`` connections can't be used across threads. ``TheadedConn`` opens a sqlite
    connection in its own thread and sends it queries through a queue, making it suitable in
    multi-threaded environment.
    """
    def __init__(self, dbname, autocommit):
        self._t = _ActualThread(dbname, autocommit)
        self.lastrowid = -1
    
    def __del__(self):
        self.close()
    
    def close(self):
        self._t.close()
    
    def commit(self):
        self._t.commit()
    
    def execute(self, sql, values=()):
        result = self._t.execute(sql, values)
        self.lastrowid = self._t.lastrowid
        return result
    
    def rollback(self):
        self._t.rollback()
    
