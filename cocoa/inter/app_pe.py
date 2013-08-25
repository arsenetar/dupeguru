# Created By: Virgil Dupras
# Created On: 2006/11/13
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import os.path as op
import plistlib
import logging
import re

from appscript import app, its, k, CommandError, ApplicationNotFoundError

from hscommon import io
from hscommon.util import remove_invalid_xml, first
from hscommon.path import Path
from hscommon.trans import trget
from cocoa import proxy

from core.scanner import ScanType
from core import directories
from core.app import JobType
from core_pe import _block_osx
from core_pe.photo import Photo as PhotoBase
from core_pe.app import DupeGuru as DupeGuruBase
from .app import PyDupeGuruBase

tr = trget('ui')

IPHOTO_PATH = Path('iPhoto Library')
APERTURE_PATH = Path('Aperture Library')

class Photo(PhotoBase):
    HANDLED_EXTS = PhotoBase.HANDLED_EXTS.copy()
    HANDLED_EXTS.update({'psd', 'nef', 'cr2', 'orf'})
    
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
    def __init__(self, path, db_id):
        # In IPhoto, we don't care about the db_id, we find photos by path.
        Photo.__init__(self, path)
    
    @property
    def display_folder_path(self):
        return IPHOTO_PATH

class AperturePhoto(Photo):
    def __init__(self, path, db_id):
        Photo.__init__(self, path)
        self.db_id = db_id
    
    @property
    def display_folder_path(self):
        return APERTURE_PATH

def get_iphoto_or_aperture_pictures(plistpath, photo_class):
    # The structure of iPhoto and Aperture libraries for the base photo list are excactly the same.
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
    for key, photo_data in plist['Master Image List'].items():
        if photo_data['MediaType'] != 'Image':
            continue
        photo_path = Path(photo_data['ImagePath'])
        photo = photo_class(photo_path, key)
        result.append(photo)
    return result

def get_iphoto_pictures(plistpath):
    return get_iphoto_or_aperture_pictures(plistpath, IPhoto)

def get_aperture_pictures(plistpath):
    return get_iphoto_or_aperture_pictures(plistpath, AperturePhoto)

def get_iapps_database_path(prefname):
    plisturls = proxy.prefValue_inDomain_(prefname, 'com.apple.iApps')
    if not plisturls:
        raise directories.InvalidPathError()
    plistpath = proxy.url2path_(plisturls[0])
    return Path(plistpath)

def get_iphoto_database_path():
    return get_iapps_database_path('iPhotoRecentDatabases')

def get_aperture_database_path():
    return get_iapps_database_path('ApertureLibraries')

class Directories(directories.Directories):
    def __init__(self):
        directories.Directories.__init__(self, fileclasses=[Photo])
        try:
            self.iphoto_libpath = get_iphoto_database_path()
            self.set_state(self.iphoto_libpath[:-1], directories.DirectoryState.Excluded)
        except directories.InvalidPathError:
            self.iphoto_libpath = None
        try:
            self.aperture_libpath = get_aperture_database_path()
            self.set_state(self.aperture_libpath[:-1], directories.DirectoryState.Excluded)
        except directories.InvalidPathError:
            self.aperture_libpath = None
    
    def _get_files(self, from_path, j):
        if from_path == IPHOTO_PATH:
            if self.iphoto_libpath is None:
                return []
            is_ref = self.get_state(from_path) == directories.DirectoryState.Reference
            photos = get_iphoto_pictures(self.iphoto_libpath)
            for photo in photos:
                photo.is_ref = is_ref
            return photos
        elif from_path == APERTURE_PATH:
            if self.aperture_libpath is None:
                return []
            is_ref = self.get_state(from_path) == directories.DirectoryState.Reference
            photos = get_aperture_pictures(self.aperture_libpath)
            for photo in photos:
                photo.is_ref = is_ref
            return photos
        else:
            return directories.Directories._get_files(self, from_path, j)
    
    @staticmethod
    def get_subfolders(path):
        if path in {IPHOTO_PATH, APERTURE_PATH}:
            return []
        else:
            return directories.Directories.get_subfolders(path)
    
    def add_path(self, path):
        if path in {IPHOTO_PATH, APERTURE_PATH}:
            if path not in self:
                self._dirs.append(path)
        else:
            directories.Directories.add_path(self, path)
    
    def has_iphoto_path(self):
        return any(path in {IPHOTO_PATH, APERTURE_PATH} for path in self._dirs)
    
    def has_any_file(self):
        # If we don't do that, it causes a hangup in the GUI when we click Start Scanning because
        # checking if there's any file to scan involves reading the whole library. If we have the
        # iPhoto library, we assume we have at least one file.
        if self.has_iphoto_path():
            return True
        else:
            return directories.Directories.has_any_file(self)
    

class DupeGuruPE(DupeGuruBase):
    def __init__(self, view, appdata):
        appdata = op.join(appdata, 'dupeGuru Picture Edition')
        DupeGuruBase.__init__(self, view, appdata)
        self.directories = Directories()
    
    def _do_delete(self, j, *args):
        def op(dupe):
            j.add_progress()
            return self._do_delete_dupe(dupe, *args)
        
        self.deleted_aperture_photos = False
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
        if any(isinstance(dupe, AperturePhoto) for dupe in marked):
            self.deleted_aperture_photos = True
            j.add_progress(0, desc=tr("Talking to Aperture. Don't touch it!"))
            try:
                a = app('Aperture')
                a.activate(timeout=0)
            except (CommandError, RuntimeError, ApplicationNotFoundError):
                pass
        self.results.perform_on_marked(op, True)
    
    def _do_delete_dupe(self, dupe, *args):
        if isinstance(dupe, IPhoto):
            try:
                a = app('iPhoto')
                album = a.photo_library_album()
                if album is None:
                    msg = "There are communication problems with iPhoto. Try opening iPhoto first, it might solve it."
                    raise EnvironmentError(msg)
                [photo] = album.photos[its.image_path == str(dupe.path)]()
                a.remove(photo, timeout=0)
            except ValueError:
                msg = "Could not find photo '{}' in iPhoto Library".format(str(dupe.path))
                raise EnvironmentError(msg)
            except (CommandError, RuntimeError) as e:
                raise EnvironmentError(str(e))
        if isinstance(dupe, AperturePhoto):
            try:
                a = app('Aperture')
                # I'm flying blind here. In my own test library, all photos are in an album with the
                # id "LibraryFolder", so I'm going to guess that it's the case at least most of the
                # time. As a safeguard, if we don't find any library with that id, we'll use the
                # first album.
                # Now, about deleting: All attempts I've made at sending photos to trash failed,
                # even with normal applescript. So, what we're going to do here is to create a
                # "dupeGuru Trash" project and tell the user to manually send those photos to trash.
                libraries = a.libraries()
                library = first(l for l in libraries if l.id == 'LibraryFolder')
                if library is None:
                    library = libraries[0]
                trash_project = a.projects["dupeGuru Trash"]
                if trash_project.exists():
                    trash_project = trash_project()
                else:
                    trash_project = library.make(new=k.project, with_properties={k.name: "dupeGuru Trash"})
                [photo] = library.image_versions[its.id == dupe.db_id]()
                photo.move(to=trash_project)
            except (IndexError, ValueError):
                msg = "Could not find photo '{}' in Aperture Library".format(str(dupe.path))
                raise EnvironmentError(msg)
            except (CommandError, RuntimeError) as e:
                raise EnvironmentError(str(e))
        else:
            DupeGuruBase._do_delete_dupe(self, dupe, *args)
    
    def _create_file(self, path):
        if (self.directories.iphoto_libpath is not None) and (path in self.directories.iphoto_libpath[:-1]):
            if not hasattr(self, 'path2iphoto'):
                photos = get_iphoto_pictures(self.directories.iphoto_libpath)
                self.path2iphoto = {p.path: p for p in photos}
            return self.path2iphoto.get(path)
        if (self.directories.aperture_libpath is not None) and (path in self.directories.aperture_libpath[:-1]):
            if not hasattr(self, 'path2aperture'):
                photos = get_aperture_pictures(self.directories.aperture_libpath)
                self.path2aperture = {p.path: p for p in photos}
            return self.path2aperture.get(path)
        return DupeGuruBase._create_file(self, path)
    
    def _job_completed(self, jobid):
        DupeGuruBase._job_completed(self, jobid)
        if jobid == JobType.Load:
            if hasattr(self, 'path2iphoto'):
                del self.path2iphoto
            if hasattr(self, 'path2aperture'):
                del self.path2aperture
        if jobid == JobType.Delete and self.deleted_aperture_photos:
            msg = tr("Deleted Aperture photos were sent to a project called \"dupeGuru Trash\".")
            self.view.show_message(msg)
    
    def copy_or_move(self, dupe, copy, destination, dest_type):
        if isinstance(dupe, (IPhoto, AperturePhoto)):
            copy = True
        return DupeGuruBase.copy_or_move(self, dupe, copy, destination, dest_type)
    
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
        if self.directories.has_iphoto_path():
            try:
                app('iPhoto')
            except ApplicationNotFoundError:
                self.view.show_message(tr("The iPhoto application couldn't be found."))
                return
        DupeGuruBase.start_scanning(self)
    
class PyDupeGuru(PyDupeGuruBase):
    def __init__(self):
        self._init(DupeGuruPE)
    
    def clearPictureCache(self):
        self.model.scanner.clear_picture_cache()
    
    #---Information    
    def getSelectedDupePath(self) -> str:
        return str(self.model.selected_dupe_path())
    
    def getSelectedDupeRefPath(self) -> str:
        return str(self.model.selected_dupe_ref_path())
    
    #---Properties
    def setScanType_(self, scan_type: int):
        try:
            self.model.scanner.scan_type = [
                ScanType.FuzzyBlock,
                ScanType.ExifTimestamp,
            ][scan_type]
        except IndexError:
            pass
    
    def setMatchScaled_(self, match_scaled: bool):
        self.model.scanner.match_scaled = match_scaled
    
    def setMinMatchPercentage_(self, percentage: int):
        self.model.scanner.threshold = percentage
