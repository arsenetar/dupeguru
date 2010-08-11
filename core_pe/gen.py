#!/usr/bin/env python
# Created By: Virgil Dupras
# Created On: 2009-05-26
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import os
import os.path as op

def move(src, dst):
    if not op.exists(src):
        return
    if op.exists(dst):
        os.remove(dst)
    print('Moving %s --> %s' % (src, dst))
    os.rename(src, dst)

os.chdir('modules')
os.system('python3 setup.py build_ext --inplace')
os.chdir('..')
move(op.join('modules', '_block.so'), '_block.so')
move(op.join('modules', '_block.pyd'), '_block.pyd')
move(op.join('modules', '_block_osx.so'), '_block_osx.so')
move(op.join('modules', '_cache.so'), '_cache.so')
move(op.join('modules', '_cache.pyd'), '_cache.pyd')
