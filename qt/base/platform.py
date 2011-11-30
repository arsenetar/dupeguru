# Created By: Virgil Dupras
# Created On: 2009-09-27
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import os.path as op
from hscommon.plat import ISWINDOWS, ISOSX, ISLINUX

# We want to get the absolute path or our root folder. We know that in that folder we're inside
# qt/base, so we just fo back two levels.
BASE_PATH = op.abspath(op.join(op.dirname(__file__), '..', '..'))
HELP_PATH = op.join(BASE_PATH, 'help')

if ISWINDOWS:
    INITIAL_FOLDER_IN_DIALOGS = 'C:\\'
elif ISOSX:
    INITIAL_FOLDER_IN_DIALOGS = '/'
elif ISLINUX:
    INITIAL_FOLDER_IN_DIALOGS = '/'
else:
    pass # unsupported platform
