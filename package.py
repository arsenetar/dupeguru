# Created By: Virgil Dupras
# Created On: 2009-12-30
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

import os
import os.path as op
import compileall
import shutil
import json
from argparse import ArgumentParser
import platform
import glob

from hscommon.plat import ISWINDOWS, ISLINUX
from hscommon.build import (
    add_to_pythonpath, print_and_do, copy_packages, build_debian_changelog,
    copy_qt_plugins, get_module_version, filereplace, copy, setup_package_argparser,
    package_cocoa_app_in_dmg, copy_all, find_in_path
)

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
    from cx_Freeze import setup, Executable
    from PyQt5.QtCore import QLibraryInfo
    add_to_pythonpath('.')
    app_version = get_module_version('core_{}'.format(edition))
    distdir = 'dist'

    if op.exists(distdir):
        shutil.rmtree(distdir)

    if not dev:
        # Copy qt plugins
        plugin_dest = distdir
        plugin_names = ['accessible', 'codecs', 'iconengines', 'imageformats']
        copy_qt_plugins(plugin_names, plugin_dest)

    # Since v4.2.3, cx_freeze started to falsely include tkinter in the package. We exclude it
    # explicitly because of that.
    options = {
        'build_exe': {
            'includes': 'atexit',
            'excludes': ['tkinter'],
            'bin_excludes': ['icudt51', 'icuin51.dll', 'icuuc51.dll'],
            'icon': 'images\\dg{0}_logo.ico'.format(edition),
            'include_msvcr': True,
        },
        'install_exe': {
            'install_dir': 'dist',
        }
    }

    executables = [
        Executable(
            'run.py',
            base='Win32GUI',
            targetDir=distdir,
            targetName={'se': 'dupeGuru', 'me': 'dupeGuru ME', 'pe': 'dupeGuru PE'}[edition] + '.exe',
        )
    ]

    setup(
        script_args=['install'],
        options=options,
        executables=executables
    )

    print("Removing useless files")
    # Debug info that cx_freeze brings in.
    for fn in glob.glob(op.join(distdir, '*', '*.pdb')):
        os.remove(fn)
    print("Copying forgotten DLLs")
    qtlibpath = QLibraryInfo.location(QLibraryInfo.LibrariesPath)
    shutil.copy(op.join(qtlibpath, 'libEGL.dll'), distdir)
    shutil.copy(find_in_path('msvcp110.dll'), distdir)
    print("Copying the rest")
    help_path = op.join('build', 'help')
    print("Copying {} to dist\\help".format(help_path))
    shutil.copytree(help_path, op.join(distdir, 'help'))
    locale_path = op.join('build', 'locale')
    print("Copying {} to dist\\locale".format(locale_path))
    shutil.copytree(locale_path, op.join(distdir, 'locale'))

    # AdvancedInstaller.com has to be in your PATH
    # this is so we don'a have to re-commit installer.aip at every version change
    installer_file = 'installer.aip'
    installer_path = op.join('qt', edition, installer_file)
    shutil.copy(installer_path, 'installer_tmp.aip')
    print_and_do('AdvancedInstaller.com /edit installer_tmp.aip /SetVersion %s' % app_version)
    print_and_do('AdvancedInstaller.com /build installer_tmp.aip -force')
    os.remove('installer_tmp.aip')
    if op.exists('installer_tmp.back.aip'):
        os.remove('installer_tmp.back.aip')

def copy_files_to_package(destpath, packages, with_so):
    # when with_so is true, we keep .so files in the package, and otherwise, we don't. We need this
    # flag because when building debian src pkg, we *don't* want .so files (they're compiled later)
    # and when we're packaging under Arch, we're packaging a binary package, so we want them.
    if op.exists(destpath):
        shutil.rmtree(destpath)
    os.makedirs(destpath)
    shutil.copy('run.py', op.join(destpath, 'run.py'))
    extra_ignores = ['*.so'] if not with_so else None
    copy_packages(packages, destpath, extra_ignores=extra_ignores)
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
    packages = ['hscommon', 'core', ed('core_{0}'), 'qtlib', 'qt', 'send2trash']
    if edition == 'me':
        packages.append('hsaudiotag')
    copy_files_to_package(srcpath, packages, with_so=False)
    if edition == 'pe':
        os.mkdir(op.join(destpath, 'modules'))
        copy_all(op.join('core_pe', 'modules', '*.*'), op.join(destpath, 'modules'))
        copy(op.join('qt', 'pe', 'modules', 'block.c'), op.join(destpath, 'modules', 'block_qt.c'))
        copy(op.join('pkg', 'debian', 'build_pe_modules.py'), op.join(destpath, 'build_pe_modules.py'))
    debdest = op.join(destpath, 'debian')
    debskel = op.join('pkg', 'debian')
    os.makedirs(debdest)
    debopts = json.load(open(op.join(debskel, ed('{}.json'))))
    for fn in ['compat', 'copyright', 'dirs', 'rules']:
        copy(op.join(debskel, fn), op.join(debdest, fn))
    filereplace(op.join(debskel, 'control'), op.join(debdest, 'control'), **debopts)
    filereplace(op.join(debskel, 'Makefile'), op.join(destpath, 'Makefile'), **debopts)
    filereplace(op.join(debskel, 'dupeguru.desktop'), op.join(debdest, ed('dupeguru_{}.desktop')), **debopts)
    changelogpath = op.join('help', ed('changelog_{}'))
    changelog_dest = op.join(debdest, 'changelog')
    project_name = debopts['pkgname']
    from_version = {'se': '2.9.2', 'me': '5.7.2', 'pe': '1.8.5'}[edition]
    build_debian_changelog(
        changelogpath, changelog_dest, project_name, from_version=from_version,
        distribution=distribution
    )
    shutil.copy(op.join('images', ed('dg{0}_logo_128.png')), srcpath)
    os.chdir(destpath)
    cmd = "dpkg-buildpackage -S"
    os.system(cmd)
    os.chdir('../..')

def package_debian(edition):
    print("Packaging for Ubuntu")
    for distribution in ['trusty', 'utopic']:
        package_debian_distribution(edition, distribution)

def package_arch(edition):
    # For now, package_arch() will only copy the source files into build/. It copies less packages
    # than package_debian because there are more python packages available in Arch (so we don't
    # need to include them).
    print("Packaging for Arch")
    ed = lambda s: s.format(edition)
    srcpath = op.join('build', ed('dupeguru-{}-arch'))
    packages = ['hscommon', 'core', ed('core_{0}'), 'qtlib', 'qt', 'send2trash']
    if edition == 'me':
        packages.append('hsaudiotag')
    copy_files_to_package(srcpath, packages, with_so=True)
    shutil.copy(op.join('images', ed('dg{}_logo_128.png')), srcpath)
    debopts = json.load(open(op.join('pkg', 'arch', ed('{}.json'))))
    filereplace(op.join('pkg', 'arch', 'dupeguru.desktop'), op.join(srcpath, ed('dupeguru-{}.desktop')), **debopts)

def package_source_tgz(edition):
    if not op.exists('deps'):
        print("Downloading PyPI dependencies")
        print_and_do('./download_deps.sh')
    print("Creating git archive")
    app_version = get_module_version('core_{}'.format(edition))
    name = 'dupeguru-{}-src-{}.tar'.format(edition, app_version)
    dest = op.join('build', name)
    print_and_do('git archive -o {} HEAD'.format(dest))
    print("Adding dependencies and wrapping up")
    print_and_do('tar -rf {} deps'.format(dest))
    print_and_do('gzip {}'.format(dest))

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
            if not args.arch_pkg:
                distname, _, _ = platform.dist()
            else:
                distname = 'arch'
            if distname == 'arch':
                package_arch(edition)
            else:
                package_debian(edition)
        else:
            print("Qt packaging only works under Windows or Linux.")

if __name__ == '__main__':
    main()

