# Created By: Virgil Dupras
# Created On: 2006/11/13
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import os.path as op
import plistlib
import logging
import re

from appscript import app, its, CommandError, ApplicationNotFoundError

from hscommon import io
from hscommon.util import remove_invalid_xml
from hscommon.path import Path
from hscommon.cocoa.objcmin import NSUserDefaults, NSURL
from hscommon.trans import tr

from core import app_cocoa, directories
from . import data, _block_osx
from .photo import Photo as PhotoBase
from .scanner import ScannerPE

IPHOTO_PATH = Path('iPhoto Library')

class Photo(PhotoBase):
    HANDLED_EXTS = PhotoBase.HANDLED_EXTS.copy()
    HANDLED_EXTS.update({'psd', 'nef', 'cr2'})
    
    def _plat_get_dimensions(self):
        return _block_osx.get_image_size(str(self.path))
    
    def _plat_get_blocks(self, block_count_per_side, orientation):
        try:
            blocks = _block_osx.getblocks(str(self.path), block_count_per_side, orientation)
        except Exception as e:
            raise IOError('The reading of "%s" failed with "%s"' % (str(self.path), str(e)))
        if not blocks:
            raise IOError('The picture %s could not be read' % str(self.path))
        return blocks
    

class IPhoto(Photo):
    @property
    def display_path(self):
        return Path(('iPhoto Library', self.name))
    
def get_iphoto_database_path():
    ud = NSUserDefaults.standardUserDefaults()
    prefs = ud.persistentDomainForName_('com.apple.iApps')
    if prefs is None:
        raise directories.InvalidPathError()
    if 'iPhotoRecentDatabases' not in prefs:
        raise directories.InvalidPathError()
    plisturl = NSURL.URLWithString_(prefs['iPhotoRecentDatabases'][0])
    return Path(plisturl.path())

def get_iphoto_pictures(plistpath):
    if not io.exists(plistpath):
        return []
    s = io.open(plistpath, 'rt', encoding='utf-8').read()
    # There was a case where a guy had 0x10 chars in his plist, causing expat errors on loading
    s = remove_invalid_xml(s, replace_with='')
    # It seems that iPhoto sometimes doesn't properly escape & chars. The regexp below is to find
    # any & char that is not a &-based entity (&amp;, &quot;, etc.). based on TextMate's XML
    # bundle's regexp
    s, count = re.subn(r'&(?![a-zA-Z0-9_-]+|#[0-9]+|#x[0-9a-fA-F]+;)', '', s)
    if count:
        logging.warning("%d invalid XML entities replacement made", count)
    plist = plistlib.readPlistFromBytes(s.encode('utf-8'))
    result = []
    for photo_data in plist['Master Image List'].values():
        if photo_data['MediaType'] != 'Image':
            continue
        photo_path = Path(photo_data['ImagePath'])
        photo = IPhoto(photo_path)
        result.append(photo)
    return result

class Directories(directories.Directories):
    def __init__(self):
        directories.Directories.__init__(self, fileclasses=[Photo])
        try:
            self.iphoto_libpath = get_iphoto_database_path()
            self.set_state(self.iphoto_libpath[:-1], directories.DirectoryState.Excluded)
        except directories.InvalidPathError:
            self.iphoto_libpath = None
    
    def _get_files(self, from_path):
        if from_path == IPHOTO_PATH:
            if self.iphoto_libpath is None:
                return []
            is_ref = self.get_state(from_path) == directories.DirectoryState.Reference
            photos = get_iphoto_pictures(self.iphoto_libpath)
            for photo in photos:
                photo.is_ref = is_ref
            return photos
        else:
            return directories.Directories._get_files(self, from_path)
    
    @staticmethod
    def get_subfolders(path):
        if path == IPHOTO_PATH:
            return []
        else:
            return directories.Directories.get_subfolders(path)
    
    def add_path(self, path):
        if path == IPHOTO_PATH:
            if path not in self:
                self._dirs.append(path)
        else:
            directories.Directories.add_path(self, path)
    
    def has_iphoto_path(self):
        return any(path == IPHOTO_PATH for path in self._dirs)
    
    def has_any_file(self):
        # If we don't do that, it causes a hangup in the GUI when we click Start Scanning because
        # checking if there's any file to scan involves reading the whole library. If we have the
        # iPhoto library, we assume we have at least one file.
        if self.has_iphoto_path():
            return True
        else:
            return directories.Directories.has_any_file(self)
    

class DupeGuruPE(app_cocoa.DupeGuru):
    def __init__(self):
        app_cocoa.DupeGuru.__init__(self, data, 'dupeGuru Picture Edition')
        self.scanner = ScannerPE()
        self.directories = Directories()
        self.scanner.cache_path = op.join(self.appdata, 'cached_pictures.db')
    
    def _do_delete(self, j, replace_with_hardlinks):
        def op(dupe):
            j.add_progress()
            return self._do_delete_dupe(dupe, replace_with_hardlinks)
        
        marked = [dupe for dupe in self.results.dupes if self.results.is_marked(dupe)]
        j.start_job(self.results.mark_count, tr("Sending dupes to the Trash"))
        if any(isinstance(dupe, IPhoto) for dupe in marked):
            j.add_progress(0, desc=tr("Talking to iPhoto. Don't touch it!"))
            try:
                a = app('iPhoto')
                a.activate(timeout=0)
                a.select(a.photo_library_album(timeout=0), timeout=0)
            except (CommandError, RuntimeError, ApplicationNotFoundError):
                pass
        self.results.perform_on_marked(op, True)
    
    def _do_delete_dupe(self, dupe, replace_with_hardlinks):
        if isinstance(dupe, IPhoto):
            try:
                a = app('iPhoto')
                [photo] = a.photo_library_album().photos[its.image_path == str(dupe.path)]()
                a.remove(photo, timeout=0)
            except ValueError:
                msg = "Could not find photo '{}' in iPhoto Library".format(str(dupe.path))
                raise EnvironmentError(msg)
            except (CommandError, RuntimeError) as e:
                raise EnvironmentError(str(e))
        else:
            app_cocoa.DupeGuru._do_delete_dupe(self, dupe, replace_with_hardlinks)
    
    def _get_file(self, str_path):
        p = Path(str_path)
        if (self.directories.iphoto_libpath is not None) and (p in self.directories.iphoto_libpath[:-1]):
            return IPhoto(p)
        return app_cocoa.DupeGuru._get_file(self, str_path)
    
    def copy_or_move(self, dupe, copy, destination, dest_type):
        if isinstance(dupe, IPhoto):
            copy = True
        return app_cocoa.DupeGuru.copy_or_move(self, dupe, copy, destination, dest_type)
    
    def selected_dupe_path(self):
        if not self.selected_dupes:
            return None
        return self.selected_dupes[0].path
    
    def selected_dupe_ref_path(self):
        if not self.selected_dupes:
            return None
        ref = self.results.get_group_of_duplicate(self.selected_dupes[0]).ref
        if ref is self.selected_dupes[0]: # we don't want the same pic to be displayed on both sides
            return None
        return ref.path
    
    def start_scanning(self):
        result = app_cocoa.DupeGuru.start_scanning(self)
        if self.directories.has_iphoto_path():
            try:
                app('iPhoto')
            except ApplicationNotFoundError:
                return 4
        return result
    
