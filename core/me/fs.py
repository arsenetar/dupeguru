# Created By: Virgil Dupras
# Created On: 2009-10-23
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from hsaudiotag import auto
from hscommon.util import get_file_ext, format_size, format_time

from core.util import format_timestamp, format_perc, format_words, format_dupe_count
from core import fs

TAG_FIELDS = {
    "audiosize",
    "duration",
    "bitrate",
    "samplerate",
    "title",
    "artist",
    "album",
    "genre",
    "year",
    "track",
    "comment",
}


class MusicFile(fs.File):
    INITIAL_INFO = fs.File.INITIAL_INFO.copy()
    INITIAL_INFO.update(
        {
            "audiosize": 0,
            "bitrate": 0,
            "duration": 0,
            "samplerate": 0,
            "artist": "",
            "album": "",
            "title": "",
            "genre": "",
            "comment": "",
            "year": "",
            "track": 0,
        }
    )
    __slots__ = fs.File.__slots__ + tuple(INITIAL_INFO.keys())

    @classmethod
    def can_handle(cls, path):
        if not fs.File.can_handle(path):
            return False
        return get_file_ext(path.name) in auto.EXT2CLASS

    def get_display_info(self, group, delta):
        size = self.size
        duration = self.duration
        bitrate = self.bitrate
        samplerate = self.samplerate
        mtime = self.mtime
        m = group.get_match_of(self)
        if m:
            percentage = m.percentage
            dupe_count = 0
            if delta:
                r = group.ref
                size -= r.size
                duration -= r.duration
                bitrate -= r.bitrate
                samplerate -= r.samplerate
                mtime -= r.mtime
        else:
            percentage = group.percentage
            dupe_count = len(group.dupes)
        dupe_folder_path = getattr(self, "display_folder_path", self.folder_path)
        return {
            "name": self.name,
            "folder_path": str(dupe_folder_path),
            "size": format_size(size, 2, 2, False),
            "duration": format_time(duration, with_hours=False),
            "bitrate": str(bitrate),
            "samplerate": str(samplerate),
            "extension": self.extension,
            "mtime": format_timestamp(mtime, delta and m),
            "title": self.title,
            "artist": self.artist,
            "album": self.album,
            "genre": self.genre,
            "year": self.year,
            "track": str(self.track),
            "comment": self.comment,
            "percentage": format_perc(percentage),
            "words": format_words(self.words) if hasattr(self, "words") else "",
            "dupe_count": format_dupe_count(dupe_count),
        }

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
