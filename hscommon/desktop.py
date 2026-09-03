# Created By: Virgil Dupras
# Created On: 2013-10-12
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

import os.path as op
from enum import Enum
from os import PathLike


class SpecialFolder(Enum):
    APPDATA = 1
    CACHE = 2


def open_url(url: str) -> None:
    """Open ``url`` with the default browser."""
    _open_url(url)


def open_path(path: PathLike) -> None:
    """Open ``path`` with its associated application."""
    _open_path(str(path))


def reveal_path(path: PathLike) -> None:
    """Open the folder containing ``path`` with the default file browser."""
    _reveal_path(str(path))


def special_folder_path(special_folder: SpecialFolder, portable: bool = False) -> str:
    """Returns the path of ``special_folder``.

    ``special_folder`` is a SpecialFolder.* const. The result is the special folder for the current
    application. The running process' application info is used to determine relevant information.

    You can override the application name with ``appname``. This argument is ingored under Qt.
    """
    return _special_folder_path(special_folder, portable=portable)


try:
    import subprocess

    from PyQt5.QtCore import QStandardPaths, QUrl
    from PyQt5.QtGui import QDesktopServices

    from core.util import executable_folder
    from hscommon.plat import ISOSX, ISWINDOWS
    from qt.util import get_appdata

    def _open_url(url: str) -> None:
        QDesktopServices.openUrl(QUrl(url))

    def _open_path(path: str) -> None:
        url = QUrl.fromLocalFile(str(path))
        QDesktopServices.openUrl(url)

    def _reveal_path(path: str) -> None:
        if ISWINDOWS:
            subprocess.run(["explorer", "/select,", op.abspath(path)])
        elif ISOSX:
            subprocess.run(["open", "-R", op.abspath(path)])
        else:
            _open_path(op.dirname(str(path)))

    def _special_folder_path(special_folder: SpecialFolder, portable: bool = False) -> str:
        if special_folder == SpecialFolder.CACHE:
            if ISWINDOWS and portable:
                folder = op.join(executable_folder(), "cache")
            else:
                folder = QStandardPaths.standardLocations(QStandardPaths.CacheLocation)[0]
        else:
            folder = get_appdata(portable)
        return folder

except ImportError:
    # Fallback for headless, web server, or environments without PyQt5
    from core.paths import get_appdata_path, get_cache_path

    def _open_url(url: str) -> None:
        # Dummy for tests/headless
        pass

    def _open_path(path: str) -> None:
        # Dummy for tests/headless
        pass

    def _reveal_path(path: str) -> None:
        # Dummy for tests/headless
        pass

    def _special_folder_path(special_folder: SpecialFolder, portable: bool = False) -> str:
        if special_folder == SpecialFolder.CACHE:
            return get_cache_path(portable=portable)
        return get_appdata_path(portable=portable)
