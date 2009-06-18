#!/usr/bin/env python
# Unit Name: gen
# Created By: Virgil Dupras
# Created On: 2009-05-26
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

import os
import os.path as op

def move(src, dst):
    if not op.exists(src):
        return
    if op.exists(dst):
        os.remove(dst)
    print 'Moving %s --> %s' % (src, dst)
    os.rename(src, dst)


os.chdir(op.join('modules', 'block'))
os.system('python setup.py build_ext --inplace')
os.chdir(op.join('..', 'cache'))
os.system('python setup.py build_ext --inplace')
os.chdir(op.join('..', '..'))
move(op.join('modules', 'block', '_block.so'), '_block.so')
move(op.join('modules', 'block', '_block.pyd'), '_block.pyd')
move(op.join('modules', 'cache', '_cache.so'), '_cache.so')
move(op.join('modules', 'cache', '_cache.pyd'), '_cache.pyd')
