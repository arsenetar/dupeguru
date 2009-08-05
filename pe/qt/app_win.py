# Created By: Virgil Dupras
# Created On: 2009-05-02
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import winshell

import app

class DupeGuru(app.DupeGuru):
    @staticmethod
    def _recycle_dupe(dupe):
        winshell.delete_file(unicode(dupe.path), no_confirm=True)
    
