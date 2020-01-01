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
            ScanOption(ScanType.Filename, tr("Filename")),
            ScanOption(ScanType.Fields, tr("Filename - Fields")),
            ScanOption(ScanType.FieldsNoOrder, tr("Filename - Fields (No Order)")),
            ScanOption(ScanType.Tag, tr("Tags")),
            ScanOption(ScanType.Contents, tr("Contents")),
        ]
