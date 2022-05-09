# Copyright 2016 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

import logging
from hscommon.util import get_file_ext, format_size

from core.util import format_timestamp, format_perc, format_dupe_count
from core import fs
from core.pe import exif

# This global value is set by the platform-specific subclasser of the Photo base class
PLAT_SPECIFIC_PHOTO_CLASS = None


def format_dimensions(dimensions):
    return "%d x %d" % (dimensions[0], dimensions[1])


def get_delta_dimensions(value, ref_value):
    return (value[0] - ref_value[0], value[1] - ref_value[1])


class Photo(fs.File):
    INITIAL_INFO = fs.File.INITIAL_INFO.copy()
    INITIAL_INFO.update({"dimensions": (0, 0), "exif_timestamp": ""})
    __slots__ = fs.File.__slots__ + tuple(INITIAL_INFO.keys())

    # These extensions are supported on all platforms
    HANDLED_EXTS = {"png", "jpg", "jpeg", "gif", "bmp", "tiff", "tif"}

    def _plat_get_dimensions(self):
        raise NotImplementedError()

    def _plat_get_blocks(self, block_count_per_side, orientation):
        raise NotImplementedError()

    def _get_orientation(self):
        if not hasattr(self, "_cached_orientation"):
            try:
                with self.path.open("rb") as fp:
                    exifdata = exif.get_fields(fp)
                    # the value is a list (probably one-sized) of ints
                    orientations = exifdata["Orientation"]
                    self._cached_orientation = orientations[0]
            except Exception:  # Couldn't read EXIF data, no transforms
                self._cached_orientation = 0
        return self._cached_orientation

    def _get_exif_timestamp(self):
        try:
            with self.path.open("rb") as fp:
                exifdata = exif.get_fields(fp)
                return exifdata["DateTimeOriginal"]
        except Exception:
            logging.info("Couldn't read EXIF of picture: %s", self.path)
        return ""

    @classmethod
    def can_handle(cls, path):
        return fs.File.can_handle(path) and get_file_ext(path.name) in cls.HANDLED_EXTS

    def get_display_info(self, group, delta):
        size = self.size
        mtime = self.mtime
        dimensions = self.dimensions
        m = group.get_match_of(self)
        if m:
            percentage = m.percentage
            dupe_count = 0
            if delta:
                r = group.ref
                size -= r.size
                mtime -= r.mtime
                dimensions = get_delta_dimensions(dimensions, r.dimensions)
        else:
            percentage = group.percentage
            dupe_count = len(group.dupes)
        dupe_folder_path = getattr(self, "display_folder_path", self.folder_path)
        return {
            "name": self.name,
            "folder_path": str(dupe_folder_path),
            "size": format_size(size, 0, 1, False),
            "extension": self.extension,
            "dimensions": format_dimensions(dimensions),
            "exif_timestamp": self.exif_timestamp,
            "mtime": format_timestamp(mtime, delta and m),
            "percentage": format_perc(percentage),
            "dupe_count": format_dupe_count(dupe_count),
        }

    def _read_info(self, field):
        fs.File._read_info(self, field)
        if field == "dimensions":
            self.dimensions = self._plat_get_dimensions()
            if self._get_orientation() in {5, 6, 7, 8}:
                self.dimensions = (self.dimensions[1], self.dimensions[0])
        elif field == "exif_timestamp":
            self.exif_timestamp = self._get_exif_timestamp()

    def get_blocks(self, block_count_per_side):
        return self._plat_get_blocks(block_count_per_side, self._get_orientation())
