# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-08-31
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from __future__ import unicode_literals

import logging

import winshell

INITIAL_FOLDER_IN_DIALOGS = 'C:\\'

def recycle_file(path):
    try:
        winshell.delete_file(unicode(path), no_confirm=True, silent=True)
    except winshell.x_winshell as e:
        logging.warning("winshell error: %s", e)
