#!/usr/bin/env python
# Created By: Virgil Dupras
# Created On: 2009-05-22
# $Id$
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

# On Windows, PyInstaller is used to build an exe (py2exe creates a very bad looking icon)
# The release version is outdated. Use at least r672 on http://svn.pyinstaller.org/trunk

import os
import os.path as op
import shutil

from hsutil.build import print_and_do
from app import DupeGuru

# Removing build and dist
if op.exists('build'):
    shutil.rmtree('build')
if op.exists('dist'):
    shutil.rmtree('dist')

version = DupeGuru.VERSION
versioncomma = version.replace('.', ', ') + ', 0'
verinfo = open('verinfo').read()
verinfo = verinfo.replace('$versioncomma', versioncomma).replace('$version', version)
fp = open('verinfo_tmp', 'w')
fp.write(verinfo)
fp.close()
print_and_do("python C:\\Python26\\pyinstaller\\Build.py dgme.spec")
os.remove('verinfo_tmp')

print_and_do("del dist\\*90.dll") # They're in vcredist, no need to include them
print_and_do("xcopy /Y /S /I help\\dupeguru_me_help dist\\help")

aicom = '"\\Program Files\\Caphyon\\Advanced Installer\\AdvancedInstaller.com"'
shutil.copy('installer.aip', 'installer_tmp.aip') # this is so we don'a have to re-commit installer.aip at every version change
print_and_do('%s /edit installer_tmp.aip /SetVersion %s' % (aicom, version))
print_and_do('%s /build installer_tmp.aip -force' % aicom)
os.remove('installer_tmp.aip')