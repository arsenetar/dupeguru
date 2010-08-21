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

from setuptools import setup
from distutils.extension import Extension
import yaml

from hscommon import helpgen
from hscommon.build import add_to_pythonpath, print_and_do, build_all_qt_ui, copy_packages

def build_cocoa(edition, dev, help_destpath):
    if not dev:
        print("Building help index")
        os.system('open -a /Developer/Applications/Utilities/Help\\ Indexer.app {0}'.format(help_destpath))
    
    print("Building dg_cocoa.plugin")
    if op.exists('build'):
        shutil.rmtree('build')
    os.mkdir('build')
    if not dev:
        specific_packages = {
            'se': ['core_se'],
            'me': ['core_me'],
            'pe': ['core_pe'],
        }[edition]
        copy_packages(['core', 'hscommon'] + specific_packages, 'build')
    cocoa_project_path = 'cocoa/{0}'.format(edition)
    shutil.copy(op.join(cocoa_project_path, 'dg_cocoa.py'), 'build')
    os.chdir('build')
    script_args = ['py2app', '-A'] if dev else ['py2app']
    setup(
        script_args = script_args,
        plugin = ['dg_cocoa.py'],
        setup_requires = ['py2app'],
    )
    os.chdir('..')
    pluginpath = op.join(cocoa_project_path, 'dg_cocoa.plugin')
    if op.exists(pluginpath):
        shutil.rmtree(pluginpath)
    shutil.move('build/dist/dg_cocoa.plugin', pluginpath)
    if dev:
        # In alias mode, the tweakings we do to the pythonpath aren't counted in. We have to
        # manually put a .pth in the plugin
        pthpath = op.join(pluginpath, 'Contents/Resources/dev.pth')
        open(pthpath, 'w').write(op.abspath('.'))
    os.chdir(cocoa_project_path)
    print("Building the XCode project")
    args = []
    if dev:
        args.append('-configuration dev')
    else:
        args.append('-configuration release')
    args = ' '.join(args)
    os.system('xcodebuild {0}'.format(args))
    os.chdir('..')

def build_qt(edition, dev):
    print("Building Qt stuff")
    build_all_qt_ui(op.join('qtlib', 'ui'))
    build_all_qt_ui(op.join('qt', 'base'))
    build_all_qt_ui(op.join('qt', edition))
    print_and_do("pyrcc4 -py3 {0} > {1}".format(op.join('qt', 'base', 'dg.qrc'), op.join('qt', 'base', 'dg_rc.py')))

def build_pe_modules(ui):
    def move(src, dst):
        if not op.exists(src):
            return
        if op.exists(dst):
            os.remove(dst)
        print('Moving %s --> %s' % (src, dst))
        os.rename(src, dst)
    
    print("Building PE Modules")
    exts = [
        Extension("_block", [op.join('core_pe', 'modules', 'block.c'), op.join('core_pe', 'modules', 'common.c')]),
        Extension("_cache", [op.join('core_pe', 'modules', 'cache.c'), op.join('core_pe', 'modules', 'common.c')]),
    ]
    if ui == 'qt':
        exts.append(Extension("_block_qt", [op.join('qt', 'pe', 'modules', 'block.c')]))
    elif ui == 'cocoa':
        exts.append(Extension(
            "_block_osx", [op.join('core_pe', 'modules', 'block_osx.m'), op.join('core_pe', 'modules', 'common.c')],
            extra_link_args=[
                "-framework", "CoreFoundation",
                "-framework", "Foundation",
                "-framework", "ApplicationServices",]
        ))
    setup(
        script_args = ['build_ext', '--inplace'],
        ext_modules = exts,
    )
    move('_block.so', op.join('core_pe', '_block.so'))
    move('_block.pyd', op.join('core_pe', '_block.pyd'))
    move('_block_osx.so', op.join('core_pe', '_block_osx.so'))
    move('_cache.so', op.join('core_pe', '_cache.so'))
    move('_cache.pyd', op.join('core_pe', '_cache.pyd'))
    move('_block_qt.so', op.join('qt', 'pe', '_block_qt.so'))
    move('_block_qt.pyd', op.join('qt', 'pe', '_block_qt.pyd'))

def main():
    conf = yaml.load(open('conf.yaml'))
    edition = conf['edition']
    ui = conf['ui']
    dev = conf['dev']
    print("Building dupeGuru {0} with UI {1}".format(edition.upper(), ui))
    if dev:
        print("Building in Dev mode")
    add_to_pythonpath('.')
    print("Generating Help")
    windows = sys.platform == 'win32'
    profile = 'win_en' if windows else 'osx_en'
    help_dir = 'help_{0}'.format(edition)
    dest_dir = 'dupeguru_{0}_help'.format(edition) if edition != 'se' else 'dupeguru_help'
    help_basepath = op.abspath(help_dir)
    help_destpath = op.abspath(op.join(help_dir, dest_dir))
    helpgen.gen(help_basepath, help_destpath, profile=profile)
    print("Building dupeGuru")
    if edition == 'pe':
        build_pe_modules(ui)
    if ui == 'cocoa':
        build_cocoa(edition, dev, help_destpath)
    elif ui == 'qt':
        build_qt(edition, dev)

if __name__ == '__main__':
    main()
