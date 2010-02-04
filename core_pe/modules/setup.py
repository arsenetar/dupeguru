# Created By: Virgil Dupras
# Created On: 2009-04-23
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import sys

from distutils.core import setup
from distutils.extension import Extension

exts = []

exts.append(Extension("_block", ["block.c", "common.c"]))
exts.append(Extension("_cache", ["cache.c", "common.c"]))

if sys.platform == 'darwin':
    exts.append(Extension(
        "_block_osx", ["block_osx.m", "common.c"],
        extra_link_args=[
            "-framework", "CoreFoundation",
            "-framework", "Foundation",
            "-framework", "ApplicationServices",
        ]))

setup(
    ext_modules = exts,
)