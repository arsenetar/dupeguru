#!/usr/bin/env python
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import os

print "Generating help"
os.chdir('help')
os.system('python -u gen.py')
os.system('/Developer/Applications/Utilities/Help\\ Indexer.app/Contents/MacOS/Help\\ Indexer dupeguru_me_help')
os.chdir('..')

print "Generating py plugin"
os.chdir('py')
os.system('python -u gen.py')
os.chdir('..')