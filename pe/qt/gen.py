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

from hsutil.build import print_and_do, build_all_qt_ui

from help import gen

build_all_qt_ui(op.join('qtlib', 'ui'))
build_all_qt_ui('base')
build_all_qt_ui('.')
os.chdir('base')
print_and_do("pyrcc4 dg.qrc > dg_rc.py")
os.chdir('..')

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

# The CC=gcc-4.0 thing is because, in Snow Leopard, gcc-4.2 can't compile these units.
os.environ['CC'] = 'gcc-4.0'
os.chdir(op.join('modules', 'block'))
os.system('python setup.py build_ext --inplace')
os.chdir(op.join('..', '..'))
move(op.join('modules', 'block', '_block.so'), op.join('.', '_block.so'))
move(op.join('modules', 'block', '_block.pyd'), op.join('.', '_block.pyd'))

os.chdir('help')
gen.generate(windows=True)
os.chdir('..')