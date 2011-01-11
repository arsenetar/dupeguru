# Created By: Virgil Dupras
# Created On: 2009-10-22
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

# This is a fork from hsfs. The reason for this fork is that hsfs has been designed for musicGuru
# and was re-used for dupeGuru. The problem is that hsfs is way over-engineered for dupeGuru,
# resulting needless complexity and memory usage. It's been a while since I wanted to do that fork,
# and I'm doing it now.

import hashlib
import logging

from hscommon import io
from hsutil.misc import nonone, flatten
from hsutil.str import get_file_ext

class FSError(Exception):
    cls_message = "An error has occured on '{name}' in '{parent}'"
    def __init__(self, fsobject, parent=None):
        message = self.cls_message
        if isinstance(fsobject, str):
            name = fsobject
        elif isinstance(fsobject, File):
            name = fsobject.name
        else:
            name = ''
        parentname = str(parent) if parent is not None else ''
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

class File:
    INITIAL_INFO = {
        'size': 0,
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
        if field in ('size', 'mtime'):
            stats = io.stat(self.path)
            self.size = nonone(stats.st_size, 0)
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
                md5 = hashlib.md5()
                CHUNK_SIZE = 8192
                filedata = fp.read(CHUNK_SIZE)
                while filedata:
                    md5.update(filedata)
                    filedata = fp.read(CHUNK_SIZE)
                self.md5 = md5.digest()
                fp.close()
            except Exception:
                pass
    
    def _read_all_info(self, attrnames=None):
        """Cache all possible info.
        
        If `attrnames` is not None, caches only attrnames.
        """
        if attrnames is None:
            attrnames = list(self.INITIAL_INFO.keys())
        for attrname in attrnames:
            if attrname not in self.__dict__:
                self._read_info(attrname)
    
    #--- Public
    @classmethod
    def can_handle(cls, path):
        return not io.islink(path) and io.isfile(path)
    
    def rename(self, newname):
        if newname == self.name:
            return
        destpath = self.path[:-1] + newname
        if io.exists(destpath):
            raise AlreadyExistsError(newname, self.path[:-1])
        try:
            io.rename(self.path, destpath)
        except EnvironmentError:
            raise OperationError(self)
        if not io.exists(destpath):
            raise OperationError(self)
        self.path = destpath
    
    #--- Properties
    @property
    def extension(self):
        return get_file_ext(self.name)
    
    @property
    def name(self):
        return self.path[-1]
    

def get_file(path, fileclasses=[File]):
    for fileclass in fileclasses:
        if fileclass.can_handle(path):
            return fileclass(path)

def get_files(path, fileclasses=[File]):
    assert all(issubclass(fileclass, File) for fileclass in fileclasses)
    def combine_paths(p1, p2):
        try:
            return p1 + p2
        except Exception:
            # This is temporary debug logging for #84.
            logging.warning("Failed to combine %r and %r.", p1, p2)
            raise
    
    try:
        paths = [combine_paths(path, name) for name in io.listdir(path)]
        result = []
        for path in paths:
            file = get_file(path, fileclasses=fileclasses)
            if file is not None:
                result.append(file)
        return result
    except EnvironmentError:
        raise InvalidPath(path)

def get_all_files(path, fileclasses=[File]):
    files = get_files(path, fileclasses=fileclasses)
    filepaths = set(f.path for f in files)
    subpaths = [path + name for name in io.listdir(path)]
    # it's possible that a folder (bundle) gets into the file list. in that case, we don't want to recurse into it
    subfolders = [p for p in subpaths if not io.islink(p) and io.isdir(p) and p not in filepaths]
    subfiles = flatten(get_all_files(subpath, fileclasses=fileclasses) for subpath in subfolders)
    return subfiles + files
