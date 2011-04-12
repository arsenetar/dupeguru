# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-09-27
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import logging
import sys

if sys.platform == 'win32':
    from .platform_win import *
elif sys.platform == 'darwin':
    from .platform_osx import *
elif sys.platform == 'linux2':
    from .platform_lnx import *
else:
    pass # unsupported platform
