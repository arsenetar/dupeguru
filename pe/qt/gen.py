#!/usr/bin/env python
# Created By: Virgil Dupras
# Created On: 2009-05-22
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import os
import os.path as op

def print_and_do(cmd):
    print cmd
    os.system(cmd)

def move(src, dst):
    if not op.exists(src):
        return
    if op.exists(dst):
        os.remove(dst)
    print 'Moving %s --> %s' % (src, dst)
    os.rename(src, dst)

os.chdir('dupeguru_pe')
print_and_do('python gen.py')
os.chdir('..')

os.chdir('base')
print_and_do('python gen.py')
os.chdir('..')

os.chdir(op.join('modules', 'block'))
os.system('python setup.py build_ext --inplace')
os.chdir(op.join('..', '..'))
move(op.join('modules', 'block', '_block.so'), op.join('.', '_block.so'))
move(op.join('modules', 'block', '_block.pyd'), op.join('.', '_block.pyd'))

print_and_do("pyuic4 details_dialog.ui > details_dialog_ui.py")
print_and_do("pyuic4 preferences_dialog.ui > preferences_dialog_ui.py")

os.chdir('help')
print_and_do('python gen.py')
os.chdir('..')