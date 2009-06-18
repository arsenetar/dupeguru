#!/usr/bin/env python

import os
import os.path as op
import shutil

from hsutil.build import print_and_do

os.chdir('dupeguru_pe')
print_and_do('python gen.py')
os.chdir('..')

if op.exists('build'):
    shutil.rmtree('build')
if op.exists('dist'):
    shutil.rmtree('dist')

print_and_do('python -u setup.py py2app -A')