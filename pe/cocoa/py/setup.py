#!/usr/bin/env python
from setuptools import setup

from hs.build import set_buildenv

set_buildenv()

setup(
    plugin=['dg_cocoa.py'],
    setup_requires=['py2app'],
)
