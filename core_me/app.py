# Created On: 2011/09/20
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from core.app import DupeGuru as DupeGuruBase
from . import data

class DupeGuru(DupeGuruBase):
    def __init__(self, view, appdata):
        DupeGuruBase.__init__(self, view, data, appdata)
    
