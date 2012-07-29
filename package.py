# Created By: Virgil Dupras
# Created On: 2009-12-30
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import os
import os.path as op
import compileall
import shutil
import json
from argparse import ArgumentParser

from hscommon.plat import ISWINDOWS, ISLINUX
from hscommon.build import (add_to_pythonpath, print_and_do, copy_packages, build_debian_changelog,
    copy_qt_plugins, get_module_version, filereplace, copy, setup_package_argparser,
    package_cocoa_app_in_dmg, copy_all)

def parse_args():
    parser = ArgumentParser()
    setup_package_argparser(parser)
    parser.add_argument('--source', action='store_true', dest='source_pkg',
        help="Build only a source debian package (Linux only).")
    return parser.parse_args()

def package_cocoa(edition, args):
    app_path = {
        'se': 'build/dupeGuru.app',
        'me': 'build/dupeGuru ME.app',
        'pe': 'build/dupeGuru PE.app',
    }[edition]
    package_cocoa_app_in_dmg(app_path, '.', args)

def package_windows(edition, dev):
    if not ISWINDOWS:
        print("Qt packaging only works under Windows.")
        return
    add_to_pythonpath('.')
    app_version = get_module_version('core_{}'.format(edition))
    distdir = 'dist'
    
    if op.exists(distdir):
        shutil.rmtree(distdir)
    
    # Since v4.2.3, cx_freeze started to falsely include tkinter in the package. We exclude it explicitly because of that.
    cmd = 'cxfreeze --base-name Win32GUI --target-dir "{0}" --target-name "{1}.exe" --icon {2} --exclude-modules tkinter run.py'
    target_name = {'se': 'dupeGuru', 'me': 'dupeGuru ME', 'pe': 'dupeGuru PE'}[edition]
    icon_path = 'images\\dg{0}_logo.ico'.format(edition)
    print_and_do(cmd.format(distdir, target_name, icon_path))
    
    if not dev:
        # Copy qt plugins
        plugin_dest = op.join(distdir, 'qt4_plugins')
        plugin_names = ['accessible', 'codecs', 'iconengines', 'imageformats']
        copy_qt_plugins(plugin_names, plugin_dest)
        
        # Compress with UPX 
        libs = [name for name in os.listdir(distdir) if op.splitext(name)[1] in ('.pyd', '.dll', '.exe')]
        for lib in libs:
            print_and_do("upx --best \"{0}\"".format(op.join(distdir, lib)))
    
    help_path = op.join('build', 'help')
    print("Copying {} to dist\\help".format(help_path))
    shutil.copytree(help_path, op.join(distdir, 'help'))
    locale_path = op.join('build', 'locale')
    print("Copying {} to dist\\locale".format(locale_path))
    shutil.copytree(locale_path, op.join(distdir, 'locale'))

    # AdvancedInstaller.com has to be in your PATH
    # this is so we don'a have to re-commit installer.aip at every version change
    installer_path = op.join('qt', edition, 'installer.aip')
    shutil.copy(installer_path, 'installer_tmp.aip')
    print_and_do('AdvancedInstaller.com /edit installer_tmp.aip /SetVersion %s' % app_version)
    print_and_do('AdvancedInstaller.com /build installer_tmp.aip -force')
    os.remove('installer_tmp.aip')
    if op.exists('installer_tmp.back.aip'):
        os.remove('installer_tmp.back.aip')

def package_debian(edition, source_pkg):
    app_version = get_module_version('core_{}'.format(edition))
    ed = lambda s: s.format(edition)
    destpath = op.join('build', 'dupeguru-{0}-{1}'.format(edition, app_version))
    if op.exists(destpath):
        shutil.rmtree(destpath)
    srcpath = op.join(destpath, 'src')
    os.makedirs(destpath)
    os.makedirs(srcpath)
    shutil.copy('run.py', op.join(srcpath, 'run.py'))
    packages = ['hscommon', 'core', ed('core_{0}'), 'qtlib', 'qt', 'send2trash', 'jobprogress']
    if edition == 'me':
        packages.append('hsaudiotag')
    copy_packages(packages, srcpath)
    if edition == 'pe':
        os.mkdir(op.join(destpath, 'modules'))
        copy_all(op.join('core_pe', 'modules', '*.*'), op.join(destpath, 'modules'))
        copy(op.join('qt', 'pe', 'modules', 'block.c'), op.join(destpath, 'modules', 'block_qt.c'))
        copy(op.join('debian', 'build_pe_modules.py'), op.join(destpath, 'build_pe_modules.py'))
    debdest = op.join(destpath, 'debian')
    os.makedirs(debdest)
    debopts = json.load(open(op.join('debian', ed('{}.json'))))
    for fn in ['compat', 'copyright', 'dirs', 'rules']:
        copy(op.join('debian', fn), op.join(debdest, fn))
    filereplace(op.join('debian', 'control'), op.join(debdest, 'control'), **debopts)
    filereplace(op.join('debian', 'Makefile'), op.join(destpath, 'Makefile'), **debopts)
    filereplace(op.join('debian', 'dupeguru.desktop'), op.join(debdest, ed('dupeguru_{}.desktop')), **debopts)
    changelogpath = op.join('help', ed('changelog_{}'))
    changelog_dest = op.join(debdest, 'changelog')
    project_name = debopts['pkgname']
    from_version = {'se': '2.9.2', 'me': '5.7.2', 'pe': '1.8.5'}[edition]
    build_debian_changelog(changelogpath, changelog_dest, project_name, from_version=from_version)
    shutil.copytree(op.join('build', 'help'), op.join(srcpath, 'help'))
    shutil.copytree(op.join('build', 'locale'), op.join(srcpath, 'locale'))
    shutil.copy(op.join('images', ed('dg{0}_logo_128.png')), srcpath)
    compileall.compile_dir(srcpath)
    os.chdir(destpath)
    cmd = "dpkg-buildpackage"
    if source_pkg:
        cmd += " -S"
    os.system(cmd)

def main():
    args = parse_args()
    conf = json.load(open('conf.json'))
    edition = conf['edition']
    ui = conf['ui']
    dev = conf['dev']
    print("Packaging dupeGuru {0} with UI {1}".format(edition.upper(), ui))
    if ui == 'cocoa':
        package_cocoa(edition, args)
    elif ui == 'qt':
        if ISWINDOWS:
            package_windows(edition, dev)
        elif ISLINUX:
            package_debian(edition, source_pkg=args.source_pkg)
        else:
            print("Qt packaging only works under Windows or Linux.")

if __name__ == '__main__':
    main()
