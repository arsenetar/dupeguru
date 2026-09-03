# Created By: Virgil Dupras
# Created On: 2013-10-12
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

import os.path as op
import subprocess
import webbrowser
from enum import Enum
from os import PathLike

from core.paths import get_appdata_path, get_cache_path
from hscommon.plat import ISOSX, ISWINDOWS


class SpecialFolder(Enum):
    APPDATA = 1
    CACHE = 2


def open_url(url: str) -> None:
    """Open ``url`` with the default browser."""
    webbrowser.open(url)


def open_path(path: PathLike) -> None:
    """Open ``path`` with its associated application."""
    p = str(path)
    if ISWINDOWS:
        subprocess.run(["start", "", p], shell=True)
    elif ISOSX:
        subprocess.run(["open", p])
    else:
        subprocess.run(["xdg-open", p])


def reveal_path(path: PathLike) -> None:
    """Open the folder containing ``path`` with the default file browser."""
    p = str(path)
    if ISWINDOWS:
        subprocess.run(["explorer", "/select,", op.abspath(p)])
    elif ISOSX:
        subprocess.run(["open", "-R", op.abspath(p)])
    else:
        folder = op.dirname(op.abspath(p)) if op.isfile(p) else op.abspath(p)
        subprocess.run(["xdg-open", folder])


def special_folder_path(special_folder: SpecialFolder, portable: bool = False) -> str:
    """Returns the path of ``special_folder`` in pure Python."""
    if special_folder == SpecialFolder.CACHE:
        return get_cache_path(portable=portable)
    return get_appdata_path(portable=portable)


# Backward-compatibility alias
_special_folder_path = special_folder_path
