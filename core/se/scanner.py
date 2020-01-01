# Copyright 2016 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from hscommon.trans import tr

from core.scanner import Scanner as ScannerBase, ScanOption, ScanType


class ScannerSE(ScannerBase):
    @staticmethod
    def get_scan_options():
        return [
            ScanOption(ScanType.Filename, tr("Filename")),
            ScanOption(ScanType.Contents, tr("Contents")),
            ScanOption(ScanType.Folders, tr("Folders")),
        ]
