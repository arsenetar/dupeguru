# Copyright 2016 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from hscommon.trans import tr

from core.scanner import Scanner as ScannerBase, ScanOption, ScanType


class ScannerME(ScannerBase):
    @staticmethod
    def _key_func(dupe):
        return (-dupe.bitrate, -dupe.size)

    @staticmethod
    def get_scan_options():
        return [
            ScanOption(ScanType.FILENAME, tr("Filename")),
            ScanOption(ScanType.FIELDS, tr("Filename - Fields")),
            ScanOption(ScanType.FIELDSNOORDER, tr("Filename - Fields (No Order)")),
            ScanOption(ScanType.TAG, tr("Tags")),
            ScanOption(ScanType.CONTENTS, tr("Contents")),
        ]
