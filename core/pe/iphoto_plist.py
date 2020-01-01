# Created By: Virgil Dupras
# Created On: 2014-03-15
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

import plistlib


class IPhotoPlistParser(plistlib._PlistParser):
    """A parser for iPhoto plists.

    iPhoto plists tend to be malformed, so we have to subclass the built-in parser to be a bit more
    lenient.
    """

    def __init__(self):
        plistlib._PlistParser.__init__(self, use_builtin_types=True, dict_type=dict)
        # For debugging purposes, we remember the last bit of data to be analyzed so that we can
        # log it in case of an exception
        self.lastdata = ""

    def get_data(self):
        self.lastdata = plistlib._PlistParser.get_data(self)
        return self.lastdata

    def end_integer(self):
        try:
            self.add_object(int(self.get_data()))
        except ValueError:
            self.add_object(0)
