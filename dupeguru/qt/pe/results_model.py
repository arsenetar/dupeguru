# Copyright 2016 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from qt.column import Column
from qt.results_model import ResultsModel as ResultsModelBase


class ResultsModel(ResultsModelBase):
    COLUMNS = [
        Column("marked", default_width=30),
        Column("name", default_width=200),
        Column("folder_path", default_width=180),
        Column("size", default_width=60),
        Column("extension", default_width=40),
        Column("dimensions", default_width=100),
        Column("exif_timestamp", default_width=120),
        Column("mtime", default_width=120),
        Column("percentage", default_width=60),
        Column("dupe_count", default_width=80),
    ]
