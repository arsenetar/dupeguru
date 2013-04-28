# Created On: 2012-03-13
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from qtlib.column import Column
from qtlib.table import Table

class IgnoreListTable(Table):
    COLUMNS = [
        Column('path1', defaultWidth=230),
        Column('path2', defaultWidth=230),
    ]
