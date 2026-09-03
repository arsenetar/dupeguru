# Copyright 2026 Tin Le (https://github.com/TinLe/de-dup)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file.

import os
from pathlib import Path
import platform
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def get_appdata_path(portable: bool = False, project_root: Optional[Path] = None) -> str:
    """Returns the platform-specific application data directory path in pure Python,

    without requiring PyQt5 or GUI dependencies.
    """
    root = project_root or PROJECT_ROOT
    if portable:
        return os.path.join(str(root), "data")

    system = platform.system()
    home = os.path.expanduser("~")

    if system == "Windows":
        appdata = os.environ.get("APPDATA")
        base = os.path.join(appdata, "de-dup") if appdata else os.path.join(home, "AppData", "Roaming", "de-dup")
        old_base = (
            os.path.join(appdata, "dupeGuru") if appdata else os.path.join(home, "AppData", "Roaming", "dupeGuru")
        )
    elif system == "Darwin":
        base = os.path.join(home, "Library", "Application Support", "de-dup")
        old_base = os.path.join(home, "Library", "Application Support", "dupeGuru")
    else:
        data_home = os.environ.get("XDG_DATA_HOME")
        base = os.path.join(data_home, "de-dup") if data_home else os.path.join(home, ".local/share", "de-dup")
        old_base = os.path.join(data_home, "dupeGuru") if data_home else os.path.join(home, ".local/share", "dupeGuru")

    if not os.path.exists(base) and os.path.exists(old_base):
        return old_base
    return base


def get_cache_path(portable: bool = False, project_root: Optional[Path] = None) -> str:
    """Returns the platform-specific cache directory path in pure Python."""
    root = project_root or PROJECT_ROOT
    if portable:
        return os.path.join(str(root), "cache")

    system = platform.system()
    home = os.path.expanduser("~")

    if system == "Windows":
        localappdata = os.environ.get("LOCALAPPDATA")
        if localappdata:
            return os.path.join(localappdata, "de-dup", "cache")
        return os.path.join(home, "AppData", "Local", "de-dup", "cache")
    elif system == "Darwin":
        return os.path.join(home, "Library", "Caches", "de-dup")
    else:
        cache_home = os.environ.get("XDG_CACHE_HOME")
        if cache_home:
            return os.path.join(cache_home, "de-dup")
        return os.path.join(home, ".cache", "de-dup")
