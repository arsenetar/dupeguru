#!/usr/bin/env python
"""
Unit Name: dupeguru.directories
Created By: Virgil Dupras
Created On: 2006/02/27
Last modified by:$Author: virgil $
Last modified on:$Date: 2009-05-28 16:02:48 +0200 (Thu, 28 May 2009) $
                 $Revision: 4388 $
Copyright 2004-2006 Hardcoded Software (http://www.hardcoded.net)
"""
import xml.dom.minidom

from hsfs import phys
import hsfs as fs
from hsutil.files import FileOrPath
from hsutil.path import Path

(STATE_NORMAL,
STATE_REFERENCE,
STATE_EXCLUDED) = range(3)

class AlreadyThereError(Exception):
    """The path being added is already in the directory list"""

class InvalidPathError(Exception):
    """The path being added is invalid"""

class Directories(object):
    #---Override
    def __init__(self):
        self._dirs = []
        self.states = {}
        self.dirclass = phys.Directory
        self.special_dirclasses = {}
    
    def __contains__(self,path):
        for d in self._dirs:
            if path in d.path:
                return True
        return False
    
    def __delitem__(self,key):
        self._dirs.__delitem__(key)
    
    def __getitem__(self,key):
        return self._dirs.__getitem__(key)
    
    def __len__(self):
        return len(self._dirs)
    
    #---Private
    def _default_state_for_path(self, path):
        # Override this in subclasses to specify the state of some special folders.
        if path[-1].startswith('.'): # hidden
            return STATE_EXCLUDED
    
    def _get_files(self, from_dir):
        from_path = from_dir.path
        state = self.GetState(from_path)
        if state == STATE_EXCLUDED:
            # Recursively get files from folders with lots of subfolder is expensive. However, there
            # might be a subfolder in this path that is not excluded. What we want to do is to skim
            # through self.states and see if we must continue, or we can stop right here to save time
            if not any(p[:len(from_path)] == from_path for p in self.states):
                return
        result = []
        for subdir in from_dir.dirs:
            for file in self._get_files(subdir):
                yield file
        if state != STATE_EXCLUDED:
            for file in from_dir.files:
                file.is_ref = state == STATE_REFERENCE
                yield file
    
    #---Public
    def add_path(self, path):
        """Adds 'path' to self, if not already there.
        
        Raises AlreadyThereError if 'path' is already in self. If path is a directory containing
        some of the directories already present in self, 'path' will be added, but all directories
        under it will be removed. Can also raise InvalidPathError if 'path' does not exist.
        """
        if path in self:
            raise AlreadyThereError
        self._dirs = [d for d in self._dirs if d.path not in path]
        try:
            dirclass = self.special_dirclasses.get(path, self.dirclass)
            d = dirclass(None, unicode(path))
            d[:] #If an InvalidPath exception has to be raised, it will be raised here
            self._dirs.append(d)
            return d
        except fs.InvalidPath:
            raise InvalidPathError
    
    def get_files(self):
        """Returns a list of all files that are not excluded.
        
        Returned files also have their 'is_ref' attr set.
        """
        for d in self._dirs:
            d.force_update()
            try:
                for file in self._get_files(d):
                    yield file
            except fs.InvalidPath:
                pass
    
    def GetState(self, path):
        """Returns the state of 'path' (One of the STATE_* const.)
        
        Raises LookupError if 'path' is not in self.
        """
        if path not in self:
            raise LookupError("The path '%s' is not in the directory list." % str(path))
        try:
            return self.states[path]
        except KeyError:
            default_state = self._default_state_for_path(path)
            if default_state is not None:
                return default_state
            parent = path[:-1]
            if parent in self:
                return self.GetState(parent)
            else:
                return STATE_NORMAL
    
    def LoadFromFile(self,infile):
        try:
            doc = xml.dom.minidom.parse(infile)
        except:
            return
        root_dir_nodes = doc.getElementsByTagName('root_directory')
        for rdn in root_dir_nodes:
            if not rdn.getAttributeNode('path'):
                    continue
            path = rdn.getAttributeNode('path').nodeValue
            try:
                self.add_path(Path(path))
            except (AlreadyThereError,InvalidPathError):
                pass
        state_nodes = doc.getElementsByTagName('state')
        for sn in state_nodes:
            if not (sn.getAttributeNode('path') and sn.getAttributeNode('value')):
                continue
            path = sn.getAttributeNode('path').nodeValue
            state = sn.getAttributeNode('value').nodeValue
            self.SetState(Path(path), int(state))
    
    def Remove(self,directory):
        self._dirs.remove(directory)
    
    def SaveToFile(self,outfile):
        with FileOrPath(outfile, 'wb') as fp:
            doc = xml.dom.minidom.Document()
            root = doc.appendChild(doc.createElement('directories'))
            for root_dir in self:
                root_dir_node = root.appendChild(doc.createElement('root_directory'))
                root_dir_node.setAttribute('path', unicode(root_dir.path).encode('utf-8'))
            for path,state in self.states.iteritems():
                state_node = root.appendChild(doc.createElement('state'))
                state_node.setAttribute('path', unicode(path).encode('utf-8'))
                state_node.setAttribute('value', str(state))
            doc.writexml(fp,'\t','\t','\n',encoding='utf-8')
    
    def SetState(self,path,state):
        try:
            if self.GetState(path) == state:
                return
            # we don't want to needlessly fill self.states. if GetState returns the same thing
            # without an explicit entry, remove that entry
            if path in self.states:
                del self.states[path]
                if self.GetState(path) == state: # no need for an entry
                    return
            self.states[path] = state
        except LookupError:
            pass
    
