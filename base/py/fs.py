# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-10-22
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

# This is a fork from hsfs. The reason for this fork is that hsfs has been designed for musicGuru
# and was re-used for dupeGuru. The problem is that hsfs is way over-engineered for dupeGuru,
# resulting needless complexity and memory usage. It's been a while since I wanted to do that fork,
# and I'm doing it now.

from __future__ import unicode_literals

import hashlib
import logging

from hsutil import io
from hsutil.misc import nonone
from hsutil.str import get_file_ext

class FSError(Exception):
    cls_message = "An error has occured on '{name}' in '{parent}'"
    def __init__(self, fsobject, parent=None):
        message = self.cls_message
        if isinstance(fsobject, basestring):
            name = fsobject
        elif isinstance(fsobject, File):
            name = fsobject.name
        else:
            name = ''
        parentname = unicode(parent) if parent is not None else ''
        Exception.__init__(self, message.format(name=name, parent=parentname))
    

class AlreadyExistsError(FSError):
    "The directory or file name we're trying to add already exists"
    cls_message = "'{name}' already exists in '{parent}'"

class InvalidPath(FSError):
    "The path of self is invalid, and cannot be worked with."
    cls_message = "'{name}' is invalid."

class InvalidDestinationError(FSError):
    """A copy/move operation has been called, but the destination is invalid."""
    cls_message = "'{name}' is an invalid destination for this operation."

class OperationError(FSError):
    """A copy/move/delete operation has been called, but the checkup after the 
    operation shows that it didn't work."""
    cls_message = "Operation on '{name}' failed."

class File(object):
    INITIAL_INFO = {
        'size': 0,
        'ctime': 0,
        'mtime': 0,
        'md5': '',
        'md5partial': '',
    }
    
    def __init__(self, path):
        self.path = path
        #This offset is where we should start reading the file to get a partial md5
        #For audio file, it should be where audio data starts
        self._md5partial_offset = 0x4000 #16Kb
        self._md5partial_size   = 0x4000 #16Kb
    
    def __getattr__(self, attrname):
        # Only called when attr is not there
        if attrname in self.INITIAL_INFO:
            try:
                self._read_info(attrname)
            except Exception as e:
                logging.warning("An error '%s' was raised while decoding '%s'", e, repr(self.path))
            try:
                return self.__dict__[attrname]
            except KeyError:
                return self.INITIAL_INFO[attrname]
        raise AttributeError()
    
    def _read_info(self, field):
        if field in ('size', 'ctime', 'mtime'):
            stats = io.stat(self.path)
            self.size = nonone(stats.st_size, 0)
            self.ctime = nonone(stats.st_ctime, 0)
            self.mtime = nonone(stats.st_mtime, 0)
        elif field == 'md5partial':
            try:
                fp = io.open(self.path, 'rb')
                offset = self._md5partial_offset
                size = self._md5partial_size
                fp.seek(offset)
                partialdata = fp.read(size)
                md5 = hashlib.md5(partialdata)
                self.md5partial = md5.digest()
                fp.close()
            except Exception:
                pass
        elif field == 'md5':
            try:
                fp = io.open(self.path, 'rb')
                filedata = fp.read()
                md5 = hashlib.md5(filedata)
                self.md5 = md5.digest()
                fp.close()
            except Exception:
                pass
    
    def _invalidate_info(self):
        for attrname in self.INITIAL_INFO:
            if attrname in self.__dict__:
                delattr(self, attrname)
    
    def _read_all_info(self, attrnames=None):
        """Cache all possible info.
        
        If `attrnames` is not None, caches only attrnames.
        """
        if attrnames is None:
            attrnames = self.INITIAL_INFO.keys()
        for attrname in attrnames:
            if attrname not in self.__dict__:
                self._read_info(attrname)
    
    #--- Public
    @classmethod
    def can_handle(cls, path):
        return io.isfile(path)
    
    def copy(self, destpath, newname=None, force=False):
        if newname is None:
            newname = self.name
        destpath = destpath + newname
        if (not force) and (io.exists(destpath)):
            raise AlreadyExistsError(self, destpath[:-1])
        try:
            io.copy(self.path, destpath)
        except EnvironmentError:
            raise OperationError(self)
        if not io.exists(destpath):
            raise OperationError(self)
    
    def move(self, destpath, newname=None, force=False):
        if newname is None:
            newname = self.name
        destpath = destpath + newname
        if io.exists(destpath):
            if force:
                io.remove(destpath)
            else:
                raise AlreadyExistsError(self, destpath[:-1])
        try:
            io.move(self.path, destpath)
        except EnvironmentError:
            raise OperationError(self)
        if not io.exists(destpath):
            raise OperationError(self)
        self.path = destpath
    
    def rename(self, newname):
        newpath = self.path[:-1] + newname
        if io.exists(newpath):
            raise AlreadyExistsError(newname, self.path[:-1])
        try:
            io.rename(self.path, newpath)
        except OSError:
            raise OperationError(self)
        self.path = newpath
    
    #--- Properties
    @property
    def extension(self):
        return get_file_ext(self.name)
    
    @property
    def name(self):
        return self.path[-1]
    

def get_files(path, fileclass=File):
    assert issubclass(fileclass, File)
    try:
        paths = [path + name for name in io.listdir(path)]
        return [fileclass(path) for path in paths if not io.islink(path) and io.isfile(path)]
    except EnvironmentError:
        raise InvalidPath(path)
