# Copyright 2016 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

import os.path as op
from hscommon.plat import ISWINDOWS, ISOSX, ISLINUX

if op.exists(__file__):
    # We want to get the absolute path or our root folder. We know that in that folder we're
    # inside qt/, so we just go back one level.
    BASE_PATH = op.abspath(op.join(op.dirname(__file__), ".."))
else:
    # Should be a frozen environment
    if ISOSX:
        BASE_PATH = op.abspath(op.join(op.dirname(__file__), "..", "..", "Resources"))
    else:
        # For others our base path is ''.
        BASE_PATH = ""
HELP_PATH = op.join(BASE_PATH, "help", "en")

if ISWINDOWS:
    INITIAL_FOLDER_IN_DIALOGS = "C:\\"
elif ISOSX:
    INITIAL_FOLDER_IN_DIALOGS = "/"
elif ISLINUX:
    INITIAL_FOLDER_IN_DIALOGS = "/"
else:
    # unsupported platform, however '/' is a good guess for a path which is available
    INITIAL_FOLDER_IN_DIALOGS = "/"
