# Created By: Virgil Dupras
# Created On: 2009-12-30
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
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
import platform

from hscommon.plat import ISWINDOWS, ISLINUX
from hscommon.build import (add_to_pythonpath, print_and_do, copy_packages, build_debian_changelog,
    copy_qt_plugins, get_module_version, filereplace, copy, setup_package_argparser,
    package_cocoa_app_in_dmg, copy_all)
from hscommon.util import find_in_path

def parse_args():
    parser = ArgumentParser()
    setup_package_argparser(parser)
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
    
    is64bit = platform.architecture()[0] == '64bit'
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
        if not is64bit: # UPX doesn't work on 64 bit
            libs = [name for name in os.listdir(distdir) if op.splitext(name)[1] in ('.pyd', '.dll', '.exe')]
            for lib in libs:
                print_and_do("upx --best \"{0}\"".format(op.join(distdir, lib)))
    
    help_path = op.join('build', 'help')
    print("Copying {} to dist\\help".format(help_path))
    shutil.copytree(help_path, op.join(distdir, 'help'))
    locale_path = op.join('build', 'locale')
    print("Copying {} to dist\\locale".format(locale_path))
    shutil.copytree(locale_path, op.join(distdir, 'locale'))
    if is64bit:
        # In 64bit mode, we don't install the VC redist as a prerequisite. We just bundle the
        # appropriate dlls.
        shutil.copy(find_in_path('msvcr100.dll'), distdir)
        shutil.copy(find_in_path('msvcp100.dll'), distdir)

    # AdvancedInstaller.com has to be in your PATH
    # this is so we don'a have to re-commit installer.aip at every version change
    installer_file = 'installer64.aip' if is64bit else 'installer.aip'
    installer_path = op.join('qt', edition, installer_file)
    shutil.copy(installer_path, 'installer_tmp.aip')
    print_and_do('AdvancedInstaller.com /edit installer_tmp.aip /SetVersion %s' % app_version)
    print_and_do('AdvancedInstaller.com /build installer_tmp.aip -force')
    os.remove('installer_tmp.aip')
    if op.exists('installer_tmp.back.aip'):
        os.remove('installer_tmp.back.aip')

def copy_source_files(destpath, packages):
    if op.exists(destpath):
        shutil.rmtree(destpath)
    os.makedirs(destpath)
    shutil.copy('run.py', op.join(destpath, 'run.py'))
    copy_packages(packages, destpath)
    os.remove(op.join(destpath, 'qt', 'run_template.py')) # It doesn't belong in the package.
    shutil.copytree(op.join('build', 'help'), op.join(destpath, 'help'))
    shutil.copytree(op.join('build', 'locale'), op.join(destpath, 'locale'))
    compileall.compile_dir(destpath)

def package_debian_distribution(edition, distribution):
    app_version = get_module_version('core_{}'.format(edition))
    version = '{}~{}'.format(app_version, distribution)
    ed = lambda s: s.format(edition)
    destpath = op.join('build', 'dupeguru-{0}-{1}'.format(edition, version))
    srcpath = op.join(destpath, 'src')
    packages = ['hscommon', 'core', ed('core_{0}'), 'qtlib', 'qt', 'send2trash', 'jobprogress']
    if edition == 'me':
        packages.append('hsaudiotag')
    copy_source_files(srcpath, packages)
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
    build_debian_changelog(changelogpath, changelog_dest, project_name, from_version=from_version,
        distribution=distribution)
    shutil.copy(op.join('images', ed('dg{0}_logo_128.png')), srcpath)
    os.chdir(destpath)
    cmd = "dpkg-buildpackage -S"
    os.system(cmd)
    os.chdir('../..')

def package_debian(edition):
    print("Packaging for Ubuntu")
    for distribution in ['precise', 'quantal', 'raring']:
        package_debian_distribution(edition, distribution)

def package_arch(edition):
    # For now, package_arch() will only copy the source files into build/. It copies less packages
    # than package_debian because there are more python packages available in Arch (so we don't
    # need to include them).
    print("Packaging for Arch")
    ed = lambda s: s.format(edition)
    srcpath = op.join('build', ed('dupeguru-{}-arch'))
    packages = ['hscommon', 'core', ed('core_{0}'), 'qtlib', 'qt', 'send2trash', 'jobprogress']
    if edition == 'me':
        packages.append('hsaudiotag')
    copy_source_files(srcpath, packages)
    shutil.copy(op.join('images', ed('dg{}_logo_128.png')), srcpath)

def package_source_tgz(edition):
    app_version = get_module_version('core_{}'.format(edition))
    name = 'dupeguru-{}-src-{}.tar.gz'.format(edition, app_version)
    dest = op.join('build', name)
    print_and_do('git archive -o {} HEAD'.format(dest))

def main():
    args = parse_args()
    conf = json.load(open('conf.json'))
    edition = conf['edition']
    ui = conf['ui']
    dev = conf['dev']
    if args.src_pkg:
        print("Creating source package for dupeGuru {}".format(edition.upper()))
        package_source_tgz(edition)
        return
    print("Packaging dupeGuru {0} with UI {1}".format(edition.upper(), ui))
    if ui == 'cocoa':
        package_cocoa(edition, args)
    elif ui == 'qt':
        if ISWINDOWS:
            package_windows(edition, dev)
        elif ISLINUX:
            distname, _, _ = platform.dist()
            if distname == 'arch':
                package_arch(edition)
            else:
                package_debian(edition)
        else:
            print("Qt packaging only works under Windows or Linux.")

if __name__ == '__main__':
    main()
