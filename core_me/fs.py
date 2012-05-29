# Created By: Virgil Dupras
# Created On: 2009-10-23
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hsaudiotag import auto
from hscommon.util import get_file_ext
from core import fs

TAG_FIELDS = {'audiosize', 'duration', 'bitrate', 'samplerate', 'title', 'artist',
    'album', 'genre', 'year', 'track', 'comment'}

class MusicFile(fs.File):
    INITIAL_INFO = fs.File.INITIAL_INFO.copy()
    INITIAL_INFO.update({
        'audiosize': 0,
        'bitrate'  : 0,
        'duration' : 0,
        'samplerate':0,
        'artist'  : '',
        'album'   : '',
        'title'   : '',
        'genre'   : '',
        'comment' : '',
        'year'    : '',
        'track'   : 0,
    })
    __slots__ = fs.File.__slots__ + tuple(INITIAL_INFO.keys())
    
    @classmethod
    def can_handle(cls, path):
        if not fs.File.can_handle(path):
            return False
        return get_file_ext(path[-1]) in auto.EXT2CLASS
    
    def _get_md5partial_offset_and_size(self):
        f = auto.File(str(self.path))
        return (f.audio_offset, f.audio_size)
    
    def _read_info(self, field):
        fs.File._read_info(self, field)
        if field in TAG_FIELDS:
            f = auto.File(str(self.path))
            self.audiosize = f.audio_size
            self.bitrate = f.bitrate
            self.duration = f.duration
            self.samplerate = f.sample_rate
            self.artist = f.artist
            self.album = f.album
            self.title = f.title
            self.genre = f.genre
            self.comment = f.comment
            self.year = f.year
            self.track = f.track
    
