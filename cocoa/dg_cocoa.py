# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.gnu.org/licenses/gpl-3.0.html

from hscommon.trans import install_gettext_trans_under_cocoa
install_gettext_trans_under_cocoa()

from cocoa.inter import PySelectableList, PyColumns, PyTable

from inter.all import *
from inter.app import PyDupeGuru

# When built under virtualenv, the dependency collector misses this module, so we have to force it
# to see the module.
import distutils.sysconfig