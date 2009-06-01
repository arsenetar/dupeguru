#!/usr/bin/env python

import os
import os.path as op
import shutil

print "Cleaning build and dist"
if op.exists('build'):
    shutil.rmtree('build')
if op.exists('dist'):
    shutil.rmtree('dist')

print "Buiding the py2app plugin"

os.system('python -u setup.py py2app')