#!/usr/bin/env python
# Unit Name: app_win
# Created By: Virgil Dupras
# Created On: 2009-05-24
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

import winshell

import app

class DupeGuru(app.DupeGuru):
    @staticmethod
    def _recycle_dupe(dupe):
        winshell.delete_file(unicode(dupe.path), no_confirm=True)
    
