#!/usr/bin/env python

import os

print "Generating help"
os.chdir('help')
os.system('python -u gen.py')
os.system('/Developer/Applications/Utilities/Help\\ Indexer.app/Contents/MacOS/Help\\ Indexer dupeguru_pe_help')
os.chdir('..')

print "Generating py plugin"
os.chdir('py')
os.system('python -u gen.py')
os.chdir('..')