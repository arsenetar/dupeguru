# Created On: 2011/09/22
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.gnu.org/licenses/gpl-3.0.html

# Yes, I know, there's the 'platform' unit for this kind of stuff, but the thing is that I got a
# crash on startup once simply for importing this module and since then I don't trust it. One day,
# I'll investigate the cause of that crash further.

import sys

ISWINDOWS = sys.platform == 'win32'
ISOSX = sys.platform == 'darwin'
ISLINUX = sys.platform.startswith('linux')