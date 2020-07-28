# Created On: 2012-03-13
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from qtlib.column import Column
from qtlib.table import Table


class IgnoreListTable(Table):
    """ Ignore list model"""

    COLUMNS = [
        Column("path1", defaultWidth=230),
        Column("path2", defaultWidth=230),
    ]
