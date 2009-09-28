# Created By: Virgil Dupras
# Created On: 2006/11/13
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import os
import os.path as op
import logging
import plistlib

import objc
from Foundation import *
from AppKit import *
from appscript import app, k

from hsutil import job, io
import hsfs as fs
from hsfs import phys, InvalidPath
from hsutil import files
from hsutil.str import get_file_ext
from hsutil.path import Path
from hsutil.cocoa import as_fetch

from dupeguru import app_cocoa, directories
from . import data, matchbase
from .cache import string_to_colors, Cache

mainBundle = NSBundle.mainBundle()
PictureBlocks = mainBundle.classNamed_('PictureBlocks')
assert PictureBlocks is not None

class Photo(phys.File):
    INITIAL_INFO = phys.File.INITIAL_INFO.copy()
    INITIAL_INFO.update({
        'dimensions': (0,0),
    })
    
    def _read_info(self, field):
        super(Photo, self)._read_info(field)
        if field == 'dimensions':
            size = PictureBlocks.getImageSize_(unicode(self.path))
            self.dimensions = (size.width, size.height)
    
    def get_blocks(self, block_count_per_side):
        try:
            blocks = PictureBlocks.getBlocksFromImagePath_blockCount_(unicode(self.path), block_count_per_side)
        except Exception, e:
            raise IOError('The reading of "%s" failed with "%s"' % (unicode(self.path), unicode(e)))
        if not blocks:
            raise IOError('The picture %s could not be read' % unicode(self.path))
        return string_to_colors(blocks)
    

class IPhoto(Photo):
    def __init__(self, parent, whole_path):
        super(IPhoto, self).__init__(parent, whole_path[-1])
        self.whole_path = whole_path
    
    def _build_path(self):
        return self.whole_path
    
    @property
    def display_path(self):
        return super(IPhoto, self)._build_path()
    

class Directory(phys.Directory):
    cls_file_class = Photo
    cls_supported_exts = ('png', 'jpg', 'jpeg', 'gif', 'psd', 'bmp', 'tiff', 'nef', 'cr2')
    
    def _fetch_subitems(self):
        subdirs, subfiles = super(Directory,self)._fetch_subitems() 
        return subdirs, [name for name in subfiles if get_file_ext(name) in self.cls_supported_exts]
    

class IPhotoLibrary(fs.Directory):
    def __init__(self, plistpath):
        self.plistpath = plistpath
        self.refpath = plistpath[:-1]
        # the AlbumData.xml file lives right in the library path
        super(IPhotoLibrary, self).__init__(None, 'iPhoto Library')
        if not io.exists(plistpath):
            raise InvalidPath(self)
    
    def _update_photo(self, photo_data):
        if photo_data['MediaType'] != 'Image':
            return
        photo_path = Path(photo_data['ImagePath'])
        subpath = photo_path[len(self.refpath):-1]
        subdir = self
        for element in subpath:
            try:
                subdir = subdir[element]
            except KeyError:
                subdir = fs.Directory(subdir, element)
        try:
            IPhoto(subdir, photo_path)
        except fs.AlreadyExistsError:
            # it's possible for 2 entries in the plist to point to the same path. Ignore one of them.
            pass
    
    def update(self):
        self.clear()
        s = open(unicode(self.plistpath)).read()
        # There was a case where a guy had 0x10 chars in his plist, causing expat errors on loading
        s = s.replace('\x10', '')
        plist = plistlib.readPlistFromString(s)
        for photo_data in plist['Master Image List'].values():
            self._update_photo(photo_data)
    
    def force_update(self): # Don't update
        pass
    

class DupeGuruPE(app_cocoa.DupeGuru):
    def __init__(self):
        app_cocoa.DupeGuru.__init__(self, data, 'dupeguru_pe', appid=5)
        self.scanner.match_factory = matchbase.AsyncMatchFactory()
        self.directories.dirclass = Directory
        self.directories.special_dirclasses[Path('iPhoto Library')] = lambda _, __: self._create_iphoto_library()
        p = op.join(self.appdata, 'cached_pictures.db')
        self.scanner.match_factory.cached_blocks = Cache(p)
    
    def _create_iphoto_library(self):
        ud = NSUserDefaults.standardUserDefaults()
        prefs = ud.persistentDomainForName_('com.apple.iApps')
        if 'iPhotoRecentDatabases' not in prefs:
            raise directories.InvalidPathError
        plisturl = NSURL.URLWithString_(prefs['iPhotoRecentDatabases'][0])
        plistpath = Path(plisturl.path())
        return IPhotoLibrary(plistpath)
    
    def _do_delete(self, j):
        def op(dupe):
            j.add_progress()
            return self._do_delete_dupe(dupe)
        
        marked = [dupe for dupe in self.results.dupes if self.results.is_marked(dupe)]
        self.path2iphoto = {}
        if any(isinstance(dupe, IPhoto) for dupe in marked):
            j = j.start_subjob([6, 4], "Probing iPhoto. Don\'t touch it during the operation!")
            a = app('iPhoto')
            a.activate(timeout=0)
            a.select(a.photo_library_album(timeout=0), timeout=0)
            photos = as_fetch(a.photo_library_album().photos, k.item)
            for photo in j.iter_with_progress(photos):
                self.path2iphoto[unicode(photo.image_path(timeout=0))] = photo
        j.start_job(self.results.mark_count, "Sending dupes to the Trash")
        self.last_op_error_count = self.results.perform_on_marked(op, True)
        del self.path2iphoto
    
    def _do_delete_dupe(self, dupe):
        if isinstance(dupe, IPhoto):
            if unicode(dupe.path) in self.path2iphoto:
                photo = self.path2iphoto[unicode(dupe.path)]
                a = app('iPhoto')
                a.remove(photo, timeout=0)
                return True
            else:
                logging.warning("Could not find photo {0} in iPhoto Library", unicode(dupe.path))
        else:
            return app_cocoa.DupeGuru._do_delete_dupe(self, dupe)
    
    def _do_load(self, j):
        self.directories.load_from_file(op.join(self.appdata, 'last_directories.xml'))
        for d in self.directories:
            if isinstance(d, IPhotoLibrary):
                d.update()
        self.results.load_from_xml(op.join(self.appdata, 'last_results.xml'), self._get_file, j)
    
    def _get_file(self, str_path):
        p = Path(str_path)
        for d in self.directories:
            result = None
            if p in d.path:
                result = d.find_path(p[d.path:])
            if isinstance(d, IPhotoLibrary) and p in d.refpath:
                result = d.find_path(p[d.refpath:])
            if result is not None:
                return result
    
    def add_directory(self, d):
        result = app_cocoa.DupeGuru.add_directory(self, d)
        if (result == 0) and (d == 'iPhoto Library'):
            [iphotolib] = [dir for dir in self.directories if dir.path == d]
            iphotolib.update()
        return result
    
    def copy_or_move(self, dupe, copy, destination, dest_type):
        if isinstance(dupe, IPhoto):
            copy = True
        return app_cocoa.DupeGuru.copy_or_move(self, dupe, copy, destination, dest_type)
    
    def start_scanning(self):
        for directory in self.directories:
            if isinstance(directory, IPhotoLibrary):
                self.directories.set_state(directory.refpath, directories.STATE_EXCLUDED)
        return app_cocoa.DupeGuru.start_scanning(self)
    
    def selected_dupe_path(self):
        if not self.selected_dupes:
            return None
        return self.selected_dupes[0].path
    
    def selected_dupe_ref_path(self):
        if not self.selected_dupes:
            return None
        ref = self.results.get_group_of_duplicate(self.selected_dupes[0]).ref
        return ref.path
    
