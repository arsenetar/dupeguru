# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from distutils.core import setup
import py2app

from hsutil.build import move_testdata_out, put_testdata_back

move_log = move_testdata_out()
try:
    setup(
        plugin = ['dg_cocoa.py'],
    )
finally:
    put_testdata_back(move_log)
