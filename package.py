# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-12-30
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import sys
import os
import os.path as op
import shutil

import yaml

from hsutil.build import build_dmg, add_to_pythonpath, print_and_do

def package_cocoa(edition):
    app_path = {
        'se': 'cocoa/se/build/release/dupeGuru.app',
        'me': 'cocoa/me/build/release/dupeGuru ME.app',
        'pe': 'cocoa/pe/build/release/dupeGuru PE.app',
    }[edition]
    build_dmg(app_path, '.')

def package_qt(edition):
    # On Windows, PyInstaller is used to build an exe (py2exe creates a very bad looking icon)
    # The release version is outdated. Use at least r672 on http://svn.pyinstaller.org/trunk
    if sys.platform != "win32":
        print "Qt packaging only works under Windows."
        return
    add_to_pythonpath('.')
    add_to_pythonpath('qt')
    add_to_pythonpath(op.join('qt', edition))
    os.chdir(op.join('qt', edition))
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
    print_and_do("python C:\\Python26\\pyinstaller\\Build.py dg{0}.spec".format(edition))
    os.remove('verinfo_tmp')

    print_and_do("del dist\\*90.dll") # They're in vcredist, no need to include them
    print_and_do("del dist\\POWRPROF.dll") # no need of that crap
    print_and_do("del dist\\SHLWAPI.dll") # no need of that crap
    print_and_do("xcopy /Y /S /I ..\\..\\help_me\\dupeguru_me_help dist\\help")

    # AdvancedInstaller.com has to be in your PATH
    # this is so we don'a have to re-commit installer.aip at every version change
    shutil.copy('installer.aip', 'installer_tmp.aip')
    print_and_do('AdvancedInstaller.com /edit installer_tmp.aip /SetVersion %s' % version)
    print_and_do('AdvancedInstaller.com /build installer_tmp.aip -force')
    os.remove('installer_tmp.aip')
    os.chdir(op.join('..', '..'))

def main():
    conf = yaml.load(open('conf.yaml'))
    edition = conf['edition']
    ui = conf['ui']
    dev = conf['dev']
    if dev:
        print "You can't package in dev mode"
        return
    print "Packaging dupeGuru {0} with UI {1}".format(edition.upper(), ui)
    if ui == 'cocoa':
        package_cocoa(edition)
    elif ui == 'qt':
        package_qt(edition)

if __name__ == '__main__':
    main()