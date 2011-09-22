# Created By: Virgil Dupras
# Created On: 2009-09-27
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hscommon.plat import ISWINDOWS, ISOSX, ISLINUX

if ISWINDOWS:
    from .platform_win import *
elif ISOSX:
    from .platform_osx import *
elif ISLINUX:
    from .platform_lnx import *
else:
    pass # unsupported platform
