# Created By: Virgil Dupras
# Created On: 2014-03-15
# Copyright 2014 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import plistlib

class IPhotoPlistParser(plistlib.PlistParser):
    """A parser for iPhoto plists.

    iPhoto plists tend to be malformed, so we have to subclass the built-in parser to be a bit more
    lenient.
    """
    def __init__(self):
        plistlib.PlistParser.__init__(self)
        # For debugging purposes, we remember the last bit of data to be analyzed so that we can
        # log it in case of an exception
        self.lastdata = ''

    def getData(self):
        self.lastdata = plistlib.PlistParser.getData(self)
        return self.lastdata

    def end_integer(self):
        try:
            self.addObject(int(self.getData()))
        except ValueError:
            self.addObject(0)
