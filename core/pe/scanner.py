# Copyright 2016 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from hscommon.trans import tr

from core.scanner import Scanner, ScanType, ScanOption

from . import matchblock, matchexif


class ScannerPE(Scanner):
    cache_path = None
    match_scaled = False

    @staticmethod
    def get_scan_options():
        return [
            ScanOption(ScanType.FUZZYBLOCK, tr("Contents")),
            ScanOption(ScanType.EXIFTIMESTAMP, tr("EXIF Timestamp")),
        ]

    def _getmatches(self, files, j):
        if self.scan_type == ScanType.FUZZYBLOCK:
            return matchblock.getmatches(
                files,
                cache_path=self.cache_path,
                threshold=self.min_match_percentage,
                match_scaled=self.match_scaled,
                j=j,
            )
        elif self.scan_type == ScanType.EXIFTIMESTAMP:
            return matchexif.getmatches(files, self.match_scaled, j)
        else:
            raise ValueError("Invalid scan type")
