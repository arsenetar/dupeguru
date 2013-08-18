# Created By: Virgil Dupras
# Created On: 2006/11/16
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import logging
import plistlib
import time
import os.path as op
from appscript import app, its, k, CommandError, ApplicationNotFoundError
from . import tunes

from cocoa import as_fetch, proxy
from hscommon.trans import trget
from hscommon.path import Path
from hscommon.util import remove_invalid_xml

from core import directories
from core.app import JobType, JOBID2TITLE
from core.scanner import ScanType
from core_me.app import DupeGuru as DupeGuruBase
from core_me import fs
from .app import PyDupeGuruBase

tr = trget('ui')

JobType.RemoveDeadTracks = 'jobRemoveDeadTracks'
JobType.ScanDeadTracks = 'jobScanDeadTracks'

JOBID2TITLE.update({
    JobType.RemoveDeadTracks: tr("Removing dead tracks from your iTunes Library"),
    JobType.ScanDeadTracks: tr("Scanning the iTunes Library"),
})

ITUNES = 'iTunes'
ITUNES_PATH = Path('iTunes Library')

def get_itunes_library(a):
    try:
        [source] = [s for s in a.sources(timeout=0) if s.kind(timeout=0) == k.library]
        [library] = source.library_playlists(timeout=0)
        return library
    except ValueError:
        logging.warning('Some unexpected iTunes configuration encountered')
        return None

class ITunesSong(fs.MusicFile):
    def __init__(self, song_data):
        path = Path(proxy.url2path_(song_data['Location']))
        fs.MusicFile.__init__(self, path)
        self.id = song_data['Track ID']
    
    def remove_from_library(self):
        try:
            a = app(ITUNES, terms=tunes)
            library = get_itunes_library(a)
            if library is None:
                return
            [song] = library.file_tracks[its.database_ID == self.id]()
            a.delete(song, timeout=0)
        except ValueError:
            msg = "Could not find song '{}' (trackid: {}) in iTunes Library".format(str(self.path), self.id)
            raise EnvironmentError(msg)
        except (CommandError, RuntimeError) as e:
            raise EnvironmentError(str(e))
    
    display_folder_path = ITUNES_PATH

def get_itunes_database_path():
    plisturls = proxy.prefValue_inDomain_('iTunesRecentDatabases', 'com.apple.iApps')
    if not plisturls:
        raise directories.InvalidPathError()
    plistpath = proxy.url2path_(plisturls[0])
    return Path(plistpath)

def get_itunes_songs(plistpath):
    if not plistpath.exists():
        return []
    s = plistpath.open('rt', encoding='utf-8').read()
    # iTunes sometimes produces XML files with invalid characters in it.
    s = remove_invalid_xml(s, replace_with='')
    plist = plistlib.readPlistFromBytes(s.encode('utf-8'))
    result = []
    for song_data in plist['Tracks'].values():
        try:
            if song_data['Track Type'] != 'File':
                continue
            song = ITunesSong(song_data)
        except KeyError: # No "Track Type", "Location" or "Track ID" key in track
            continue
        if song.path.exists():
            result.append(song)
    return result

class Directories(directories.Directories):
    def __init__(self, fileclasses):
        directories.Directories.__init__(self, fileclasses)
        try:
            self.itunes_libpath = get_itunes_database_path()
        except directories.InvalidPathError:
            self.itunes_libpath = None
    
    def _get_files(self, from_path, j):
        if from_path == ITUNES_PATH:
            if self.itunes_libpath is None:
                return []
            is_ref = self.get_state(from_path) == directories.DirectoryState.Reference
            songs = get_itunes_songs(self.itunes_libpath)
            for song in songs:
                song.is_ref = is_ref
            return songs
        else:
            return directories.Directories._get_files(self, from_path, j)
    
    @staticmethod
    def get_subfolders(path):
        if path == ITUNES_PATH:
            return []
        else:
            return directories.Directories.get_subfolders(path)
    
    def add_path(self, path):
        if path == ITUNES_PATH:
            if path not in self:
                self._dirs.append(path)
        else:
            directories.Directories.add_path(self, path)
    
    def has_itunes_path(self):
        return any(path == ITUNES_PATH for path in self._dirs)
    
    def has_any_file(self):
        # If we don't do that, it causes a hangup in the GUI when we click Start Scanning because
        # checking if there's any file to scan involves reading the whole library. If we have the
        # iTunes library, we assume we have at least one file.
        if self.has_itunes_path():
            return True
        else:
            return directories.Directories.has_any_file(self)
    

class DupeGuruME(DupeGuruBase):
    def __init__(self, view, appdata):
        appdata = op.join(appdata, 'dupeGuru Music Edition')
        DupeGuruBase.__init__(self, view, appdata)
        # Use fileclasses set in DupeGuruBase.__init__()
        self.directories = Directories(fileclasses=self.directories.fileclasses)
        self.dead_tracks = []
    
    def _do_delete(self, j, *args):
        # XXX If I read correctly, Python 3.3 will allow us to go fetch inner function easily, so
        # we'll be able to replace "op" below with DupeGuruBase._do_delete.op.
        def op(dupe):
            j.add_progress()
            return self._do_delete_dupe(dupe, *args)
        
        marked = [dupe for dupe in self.results.dupes if self.results.is_marked(dupe)]
        j.start_job(self.results.mark_count, tr("Sending dupes to the Trash"))
        if any(isinstance(dupe, ITunesSong) for dupe in marked):
            j.add_progress(0, desc=tr("Talking to iTunes. Don't touch it!"))
            try:
                a = app(ITUNES, terms=tunes)
                a.activate(timeout=0)
            except (CommandError, RuntimeError, ApplicationNotFoundError):
                pass
        self.results.perform_on_marked(op, True)
    
    def _do_delete_dupe(self, dupe, *args):
        if isinstance(dupe, ITunesSong):
            dupe.remove_from_library()
        DupeGuruBase._do_delete_dupe(self, dupe, *args)
    
    def _create_file(self, path):
        if (self.directories.itunes_libpath is not None) and (path in self.directories.itunes_libpath[:-1]):
            if not hasattr(self, 'itunes_songs'):
                songs = get_itunes_songs(self.directories.itunes_libpath)
                self.itunes_songs = {song.path: song for song in songs}
            if path in self.itunes_songs:
                return self.itunes_songs[path]
            else:
                pass # We'll return the default file type, as per the last line of this method
        return DupeGuruBase._create_file(self, path)
    
    def _job_completed(self, jobid, exc):
        if (jobid in {JobType.RemoveDeadTracks, JobType.ScanDeadTracks}) and (exc is not None):
            msg = tr("There were communication problems with iTunes. The operation couldn't be completed.")
            self.view.show_message(msg)
            return True
        if jobid == JobType.ScanDeadTracks:
            dead_tracks_count = len(self.dead_tracks)
            if dead_tracks_count > 0:
                msg = tr("Your iTunes Library contains %d dead tracks ready to be removed. Continue?")
                if self.view.ask_yes_no(msg % dead_tracks_count):
                    self.remove_dead_tracks()
            else:
                msg = tr("You have no dead tracks in your iTunes Library")
                self.view.show_message(msg)
        if jobid == JobType.Load:
            if hasattr(self, 'itunes_songs'):
                # If we load another file, we want a refresh song list
                del self.itunes_songs
        DupeGuruBase._job_completed(self, jobid, exc)
    
    def copy_or_move(self, dupe, copy, destination, dest_type):
        if isinstance(dupe, ITunesSong):
            copy = True
        return DupeGuruBase.copy_or_move(self, dupe, copy, destination, dest_type)
    
    def start_scanning(self):
        if self.directories.has_itunes_path():
            try:
                app(ITUNES, terms=tunes)
            except ApplicationNotFoundError:
                self.view.show_message(tr("The iTunes application couldn't be found."))
                return
        DupeGuruBase.start_scanning(self)
    
    def remove_dead_tracks(self):
        def do(j):
            a = app(ITUNES, terms=tunes)
            a.activate(timeout=0)
            for index, track in enumerate(j.iter_with_progress(self.dead_tracks)):
                if index % 100 == 0:
                    time.sleep(.1)
                try:
                    track.delete(timeout=0)
                except CommandError as e:
                    logging.warning('Error while trying to remove a track from iTunes: %s' % str(e))
        
        self.view.start_job(JobType.RemoveDeadTracks, do)
    
    def scan_dead_tracks(self):
        def do(j):
            a = app(ITUNES, terms=tunes)
            a.activate(timeout=0)
            library = get_itunes_library(a)
            if library is None:
                return
            self.dead_tracks = []
            tracks = as_fetch(library.file_tracks, k.file_track)
            for index, track in enumerate(j.iter_with_progress(tracks)):
                if index % 100 == 0:
                    time.sleep(.1)
                if track.location(timeout=0) == k.missing_value:
                    self.dead_tracks.append(track)
            logging.info('Found %d dead tracks' % len(self.dead_tracks))
        
        self.view.start_job(JobType.ScanDeadTracks, do)
    
class PyDupeGuru(PyDupeGuruBase):
    def __init__(self):
        self._init(DupeGuruME)
    
    def scanDeadTracks(self):
        self.model.scan_dead_tracks()
    
    #---Properties
    def setMinMatchPercentage_(self, percentage: int):
        self.model.scanner.min_match_percentage = percentage
    
    def setScanType_(self, scan_type: int):
        try:
            self.model.scanner.scan_type = [
                ScanType.Filename,
                ScanType.Fields,
                ScanType.FieldsNoOrder,
                ScanType.Tag,
                ScanType.Contents,
                ScanType.ContentsAudio,
            ][scan_type]
        except IndexError:
            pass
    
    def setWordWeighting_(self, words_are_weighted: bool):
        self.model.scanner.word_weighting = words_are_weighted
    
    def setMatchSimilarWords_(self, match_similar_words: bool):
        self.model.scanner.match_similar_words = match_similar_words
    
    def enable_scanForTag_(self, enable: bool, scan_tag: str):
        if enable:
            self.model.scanner.scanned_tags.add(scan_tag)
        else:
            self.model.scanner.scanned_tags.discard(scan_tag)
