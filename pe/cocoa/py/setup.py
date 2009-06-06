#!/usr/bin/env python

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
