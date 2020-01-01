# Created On: 2011-11-27
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from hscommon.gui.column import Column
from hscommon.trans import trget

from core.gui.result_table import ResultTable as ResultTableBase

coltr = trget("columns")


class ResultTable(ResultTableBase):
    COLUMNS = [
        Column("marked", ""),
        Column("name", coltr("Filename")),
        Column("folder_path", coltr("Folder"), visible=False, optional=True),
        Column("size", coltr("Size (MB)"), optional=True),
        Column("duration", coltr("Time"), optional=True),
        Column("bitrate", coltr("Bitrate"), optional=True),
        Column("samplerate", coltr("Sample Rate"), visible=False, optional=True),
        Column("extension", coltr("Kind"), optional=True),
        Column("mtime", coltr("Modification"), visible=False, optional=True),
        Column("title", coltr("Title"), visible=False, optional=True),
        Column("artist", coltr("Artist"), visible=False, optional=True),
        Column("album", coltr("Album"), visible=False, optional=True),
        Column("genre", coltr("Genre"), visible=False, optional=True),
        Column("year", coltr("Year"), visible=False, optional=True),
        Column("track", coltr("Track Number"), visible=False, optional=True),
        Column("comment", coltr("Comment"), visible=False, optional=True),
        Column("percentage", coltr("Match %"), optional=True),
        Column("words", coltr("Words Used"), visible=False, optional=True),
        Column("dupe_count", coltr("Dupe Count"), visible=False, optional=True),
    ]
    DELTA_COLUMNS = {"size", "duration", "bitrate", "samplerate", "mtime"}
