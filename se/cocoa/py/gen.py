#!/usr/bin/env python
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import os
import os.path as op
import shutil

from hsutil.build import print_and_do

if op.exists('build'):
    shutil.rmtree('build')
if op.exists('dist'):
    shutil.rmtree('dist')

print_and_do('python -u setup.py py2app')