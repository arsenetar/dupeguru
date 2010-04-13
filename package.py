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
import compileall
import shutil

import yaml

from hsutil.build import (build_dmg, add_to_pythonpath, print_and_do, copy_packages,
    build_debian_changelog, copy_qt_plugins)

def package_cocoa(edition):
    app_path = {
        'se': 'cocoa/se/build/release/dupeGuru.app',
        'me': 'cocoa/me/build/release/dupeGuru ME.app',
        'pe': 'cocoa/pe/build/release/dupeGuru PE.app',
    }[edition]
    build_dmg(app_path, '.')

def package_windows(edition, dev):
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
    
    if op.exists('dist'):
        shutil.rmtree('dist')
    
    cmd = 'cxfreeze --base-name Win32GUI --target-name "{0}.exe" --icon {1} start.py'
    target_name = {'se': 'dupeGuru', 'me': 'dupeGuru ME', 'pe': 'dupeGuru PE'}[edition]
    icon_path = '..\\..\\images\\dg{0}_logo.ico'.format(edition)
    print_and_do(cmd.format(target_name, icon_path))
    
    if not dev:
        # Copy qt plugins
        plugin_dest = op.join('dist', 'qt4_plugins')
        plugin_names = ['accessible', 'codecs', 'iconengines', 'imageformats']
        copy_qt_plugins(plugin_names, plugin_dest)
        
        # Compress with UPX 
        libs = [name for name in os.listdir('dist') if op.splitext(name)[1] in ('.pyd', '.dll', '.exe')]
        for lib in libs:
            print_and_do("upx --best \"dist\\{0}\"".format(lib))
    
    help_basedir = '..\\..\\help_{0}'.format(edition)
    help_dir = 'dupeguru_{0}_help'.format(edition) if edition != 'se' else 'dupeguru_help'
    help_path = op.join(help_basedir, help_dir)
    print "Copying {0} to dist\\help".format(help_path)
    shutil.copytree(help_path, 'dist\\help')

    # AdvancedInstaller.com has to be in your PATH
    # this is so we don'a have to re-commit installer.aip at every version change
    shutil.copy('installer.aip', 'installer_tmp.aip')
    print_and_do('AdvancedInstaller.com /edit installer_tmp.aip /SetVersion %s' % DupeGuru.VERSION)
    print_and_do('AdvancedInstaller.com /build installer_tmp.aip -force')
    os.remove('installer_tmp.aip')
    os.chdir(op.join('..', '..'))

def package_debian(edition):
    add_to_pythonpath('qt')
    add_to_pythonpath(op.join('qt', edition))
    from app import DupeGuru
    
    if op.exists('build'):
        shutil.rmtree('build')
    ed = lambda s: s.format(edition)
    destpath = op.join('build', 'dupeguru-{0}-{1}'.format(edition, DupeGuru.VERSION))
    srcpath = op.join(destpath, 'src')
    help_src = ed('help_{0}')
    os.makedirs(destpath)
    shutil.copytree(ed('qt/{0}'), srcpath)
    packages = ['hsutil', 'hsgui', 'core', ed('core_{0}'), 'qtlib', 'qt/base']
    if edition == 'me':
        packages.append('hsmedia')
    copy_packages(packages, srcpath)
    # We also have to copy the Send2Trash package
    import send2trash
    pkg_path = op.dirname(send2trash.__file__)
    shutil.copytree(pkg_path, op.join(srcpath, 'send2trash'))
    shutil.copytree(ed('debian_{0}'), op.join(destpath, 'debian'))
    yaml_path = op.join(help_src, 'changelog.yaml')
    changelog_dest = op.join(destpath, 'debian', 'changelog')
    project_name = ed('dupeguru-{0}')
    from_version = {'se': '2.9.2', 'me': '5.7.2', 'pe': '1.8.5'}[edition]
    build_debian_changelog(yaml_path, changelog_dest, project_name, from_version=from_version)
    help_name = {'se': 'dupeguru_help', 'me': 'dupeguru_me_help', 'pe': 'dupeguru_pe_help'}[edition]
    shutil.copytree(op.join(help_src, help_name), op.join(srcpath, 'help'))
    shutil.copy(op.join('images', ed('dg{0}_logo_128.png')), srcpath)
    compileall.compile_dir(srcpath)
    os.chdir(destpath)
    os.system("dpkg-buildpackage")

def main():
    conf = yaml.load(open('conf.yaml'))
    edition = conf['edition']
    ui = conf['ui']
    dev = conf['dev']
    print "Packaging dupeGuru {0} with UI {1}".format(edition.upper(), ui)
    if ui == 'cocoa':
        package_cocoa(edition)
    elif ui == 'qt':
        if sys.platform == "win32":
            package_windows(edition, dev)
        elif sys.platform == "linux2":
            package_debian(edition)
        else:
            print "Qt packaging only works under Windows or Linux."

if __name__ == '__main__':
    main()
