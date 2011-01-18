# Created By: Virgil Dupras
# Created On: 2006/11/16
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import logging
from appscript import app, k, CommandError
import time

from hscommon.cocoa import as_fetch
from hscommon.trans import tr

from core.app_cocoa import JOBID2TITLE, DupeGuru as DupeGuruBase

from . import data, scanner, fs

JOB_REMOVE_DEAD_TRACKS = 'jobRemoveDeadTracks'
JOB_SCAN_DEAD_TRACKS = 'jobScanDeadTracks'

JOBID2TITLE.update({
    JOB_REMOVE_DEAD_TRACKS: tr("Removing dead tracks from your iTunes Library"),
    JOB_SCAN_DEAD_TRACKS: tr("Scanning the iTunes Library"),
})

class DupeGuruME(DupeGuruBase):
    def __init__(self):
        DupeGuruBase.__init__(self, data, 'dupeGuru Music Edition')
        self.scanner = scanner.ScannerME()
        self.directories.fileclasses = [fs.MusicFile]
        self.dead_tracks = []
    
    def remove_dead_tracks(self):
        def do(j):
            a = app('iTunes')
            a.activate(timeout=0)
            for index, track in enumerate(j.iter_with_progress(self.dead_tracks)):
                if index % 100 == 0:
                    time.sleep(.1)
                try:
                    track.delete(timeout=0)
                except CommandError as e:
                    logging.warning('Error while trying to remove a track from iTunes: %s' % str(e))
        
        self._start_job(JOB_REMOVE_DEAD_TRACKS, do)
    
    def scan_dead_tracks(self):
        def do(j):
            a = app('iTunes')
            a.activate(timeout=0)
            try:
                [source] = [s for s in a.sources(timeout=0) if s.kind(timeout=0) == k.library]
                [library] = source.library_playlists(timeout=0)
            except ValueError:
                logging.warning('Some unexpected iTunes configuration encountered')
                return
            self.dead_tracks = []
            tracks = as_fetch(library.file_tracks, k.file_track)
            for index, track in enumerate(j.iter_with_progress(tracks)):
                if index % 100 == 0:
                    time.sleep(.1)
                if track.location(timeout=0) == k.missing_value:
                    self.dead_tracks.append(track)
            logging.info('Found %d dead tracks' % len(self.dead_tracks))
        
        self._start_job(JOB_SCAN_DEAD_TRACKS, do)
    
