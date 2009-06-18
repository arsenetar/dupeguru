#!/usr/bin/env python
# Created By: Virgil Dupras
# Created On: 2009-04-23
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

setup(
    cmdclass = {'build_ext': build_ext},
    ext_modules = [Extension("_block", ["block.pyx"])]
)