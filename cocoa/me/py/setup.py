# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import os.path as op
import sys
sys.path.insert(0, op.abspath('../../..')) # for all cross-toolkit modules

from distutils.core import setup
import py2app

setup(
    plugin = ['dg_cocoa.py'],
)
