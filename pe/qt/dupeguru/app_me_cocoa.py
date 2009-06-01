#!/usr/bin/env python
"""
Unit Name: dupeguru.app_me_cocoa
Created By: Virgil Dupras
Created On: 2006/11/16
Last modified by:$Author: virgil $
Last modified on:$Date: 2009-05-28 16:33:32 +0200 (Thu, 28 May 2009) $
                 $Revision: 4392 $
Copyright 2006 Hardcoded Software (http://www.hardcoded.net)
"""
import os.path as op
import logging
from appscript import app, k, CommandError
import time

from hsutil.cocoa import as_fetch
import hsfs.phys.music

import app_cocoa, data_me, scanner

JOB_REMOVE_DEAD_TRACKS = 'jobRemoveDeadTracks'
JOB_SCAN_DEAD_TRACKS = 'jobScanDeadTracks'

app_cocoa.JOBID2TITLE.update({
    JOB_REMOVE_DEAD_TRACKS: "Removing dead tracks from your iTunes Library",
    JOB_SCAN_DEAD_TRACKS: "Scanning the iTunes Library",
})

class DupeGuruME(app_cocoa.DupeGuru):
    def __init__(self):
        app_cocoa.DupeGuru.__init__(self, data_me, 'dupeguru_me', appid=1)
        self.scanner = scanner.ScannerME()
        self.directories.dirclass = hsfs.phys.music.Directory
        self.dead_tracks = []
    
    def remove_dead_tracks(self):
        def do(j):
            a = app('iTunes')
            for index, track in enumerate(j.iter_with_progress(self.dead_tracks)):
                if index % 100 == 0:
                    time.sleep(.1)
                try:
                    track.delete()
                except CommandError as e:
                    logging.warning('Error while trying to remove a track from iTunes: %s' % unicode(e))
        
        self._start_job(JOB_REMOVE_DEAD_TRACKS, do)
    
    def scan_dead_tracks(self):
        def do(j):
            a = app('iTunes')
            try:
                [source] = [s for s in a.sources() if s.kind() == k.library]
                [library] = source.library_playlists()
            except ValueError:
                logging.warning('Some unexpected iTunes configuration encountered')
                return
            self.dead_tracks = []
            tracks = as_fetch(library.file_tracks, k.file_track)
            for index, track in enumerate(j.iter_with_progress(tracks)):
                if index % 100 == 0:
                    time.sleep(.1)
                if track.location() == k.missing_value:
                    self.dead_tracks.append(track)
            logging.info('Found %d dead tracks' % len(self.dead_tracks))
        
        self._start_job(JOB_SCAN_DEAD_TRACKS, do)
    
