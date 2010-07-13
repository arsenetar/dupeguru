# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-10-23
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from hsaudiotag import mpeg, wma, mp4, ogg, flac, aiff
from hsutil.str import get_file_ext
from core import fs

TAG_FIELDS = ['audiosize', 'duration', 'bitrate', 'samplerate', 'title', 'artist',
    'album', 'genre', 'year', 'track', 'comment']

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
    HANDLED_EXTS = set()
    
    @classmethod
    def can_handle(cls, path):
        if not fs.File.can_handle(path):
            return False
        return get_file_ext(path[-1]) in cls.HANDLED_EXTS
    

class Mp3File(MusicFile):
    HANDLED_EXTS = set(['mp3'])
    def _read_info(self, field):
        if field == 'md5partial':
            fileinfo = mpeg.Mpeg(unicode(self.path))
            self._md5partial_offset = fileinfo.audio_offset
            self._md5partial_size = fileinfo.audio_size
        MusicFile._read_info(self, field)
        if field in TAG_FIELDS:
            fileinfo = mpeg.Mpeg(unicode(self.path))
            self.audiosize = fileinfo.audio_size
            self.bitrate = fileinfo.bitrate
            self.duration = fileinfo.duration
            self.samplerate = fileinfo.sample_rate
            i1 = fileinfo.id3v1
            # id3v1, even when non-existant, gives empty values. not id3v2. if id3v2 don't exist,
            # just replace it with id3v1
            i2 = fileinfo.id3v2
            if not i2.exists:
                i2 = i1
            self.artist = i2.artist or i1.artist
            self.album = i2.album or i1.album
            self.title = i2.title or i1.title
            self.genre = i2.genre or i1.genre
            self.comment = i2.comment or i1.comment
            self.year = i2.year or i1.year
            self.track = i2.track or i1.track

class WmaFile(MusicFile):
    HANDLED_EXTS = set(['wma'])
    def _read_info(self, field):
        if field == 'md5partial':
            dec = wma.WMADecoder(unicode(self.path))
            self._md5partial_offset = dec.audio_offset
            self._md5partial_size = dec.audio_size
        MusicFile._read_info(self, field)
        if field in TAG_FIELDS:
            dec = wma.WMADecoder(unicode(self.path))
            self.audiosize = dec.audio_size
            self.bitrate = dec.bitrate
            self.duration = dec.duration
            self.samplerate = dec.sample_rate
            self.artist = dec.artist
            self.album = dec.album
            self.title = dec.title
            self.genre = dec.genre
            self.comment = dec.comment
            self.year = dec.year
            self.track = dec.track

class Mp4File(MusicFile):
    HANDLED_EXTS = set(['m4a', 'm4p'])
    def _read_info(self, field):
        if field == 'md5partial':
            dec = mp4.File(unicode(self.path))
            self._md5partial_offset = dec.audio_offset
            self._md5partial_size = dec.audio_size
            dec.close()
        MusicFile._read_info(self, field)
        if field in TAG_FIELDS:
            dec = mp4.File(unicode(self.path))
            self.audiosize = dec.audio_size
            self.bitrate = dec.bitrate
            self.duration = dec.duration
            self.samplerate = dec.sample_rate
            self.artist = dec.artist
            self.album = dec.album
            self.title = dec.title
            self.genre = dec.genre
            self.comment = dec.comment
            self.year = dec.year
            self.track = dec.track
            dec.close()

class OggFile(MusicFile):
    HANDLED_EXTS = set(['ogg'])
    def _read_info(self, field):
        if field == 'md5partial':
            dec = ogg.Vorbis(unicode(self.path))
            self._md5partial_offset = dec.audio_offset
            self._md5partial_size = dec.audio_size
        MusicFile._read_info(self, field)
        if field in TAG_FIELDS:
            dec = ogg.Vorbis(unicode(self.path))
            self.audiosize = dec.audio_size
            self.bitrate = dec.bitrate
            self.duration = dec.duration
            self.samplerate = dec.sample_rate
            self.artist = dec.artist
            self.album = dec.album
            self.title = dec.title
            self.genre = dec.genre
            self.comment = dec.comment
            self.year = dec.year
            self.track = dec.track

class FlacFile(MusicFile):
    HANDLED_EXTS = set(['flac'])
    def _read_info(self, field):
        if field == 'md5partial':
            dec = flac.FLAC(unicode(self.path))
            self._md5partial_offset = dec.audio_offset
            self._md5partial_size = dec.audio_size
        MusicFile._read_info(self, field)
        if field in TAG_FIELDS:
            dec = flac.FLAC(unicode(self.path))
            self.audiosize = dec.audio_size
            self.bitrate = dec.bitrate
            self.duration = dec.duration
            self.samplerate = dec.sample_rate
            self.artist = dec.artist
            self.album = dec.album
            self.title = dec.title
            self.genre = dec.genre
            self.comment = dec.comment
            self.year = dec.year
            self.track = dec.track

class AiffFile(MusicFile):
    HANDLED_EXTS = set(['aif', 'aiff', 'aifc'])
    def _read_info(self, field):
        if field == 'md5partial':
            dec = aiff.File(unicode(self.path))
            self._md5partial_offset = dec.audio_offset
            self._md5partial_size = dec.audio_size
        MusicFile._read_info(self, field)
        if field in TAG_FIELDS:
            dec = aiff.File(unicode(self.path))
            self.audiosize = dec.audio_size
            self.bitrate = dec.bitrate
            self.duration = dec.duration
            self.samplerate = dec.sample_rate
            tag = dec.tag
            if tag is not None:
                self.artist = tag.artist
                self.album = tag.album
                self.title = tag.title
                self.genre = tag.genre
                self.comment = tag.comment
                self.year = tag.year
                self.track = tag.track
    
