# Copyright 2017 Virgil Dupras
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

import sys
import os
import os.path as op
import compileall
import shutil
import json
from argparse import ArgumentParser
import platform
import re

from hscommon.build import (
    print_and_do, copy_packages, build_debian_changelog,
    get_module_version, filereplace, copy, setup_package_argparser,
    copy_all
)

def parse_args():
    parser = ArgumentParser()
    setup_package_argparser(parser)
    return parser.parse_args()

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

def package_debian_distribution(distribution):
    app_version = get_module_version('core')
    version = '{}~{}'.format(app_version, distribution)
    destpath = op.join('build', 'dupeguru-{}'.format(version))
    srcpath = op.join(destpath, 'src')
    packages = [
        'hscommon', 'core', 'qtlib', 'qt', 'send2trash', 'hsaudiotag'
    ]
    copy_files_to_package(srcpath, packages, with_so=False)
    os.mkdir(op.join(destpath, 'modules'))
    copy_all(op.join('core', 'pe', 'modules', '*.*'), op.join(destpath, 'modules'))
    copy(op.join('qt', 'pe', 'modules', 'block.c'), op.join(destpath, 'modules', 'block_qt.c'))
    copy(op.join('pkg', 'debian', 'build_pe_modules.py'), op.join(destpath, 'build_pe_modules.py'))
    debdest = op.join(destpath, 'debian')
    debskel = op.join('pkg', 'debian')
    os.makedirs(debdest)
    debopts = json.load(open(op.join(debskel, 'dupeguru.json')))
    for fn in ['compat', 'copyright', 'dirs', 'rules']:
        copy(op.join(debskel, fn), op.join(debdest, fn))
    filereplace(op.join(debskel, 'control'), op.join(debdest, 'control'), **debopts)
    filereplace(op.join(debskel, 'Makefile'), op.join(destpath, 'Makefile'), **debopts)
    filereplace(op.join(debskel, 'dupeguru.desktop'), op.join(debdest, 'dupeguru.desktop'), **debopts)
    changelogpath = op.join('help', 'changelog')
    changelog_dest = op.join(debdest, 'changelog')
    project_name = debopts['pkgname']
    from_version = '2.9.2'
    build_debian_changelog(
        changelogpath, changelog_dest, project_name, from_version=from_version,
        distribution=distribution
    )
    shutil.copy(op.join('images', 'dgse_logo_128.png'), srcpath)
    os.chdir(destpath)
    cmd = "dpkg-buildpackage -S"
    os.system(cmd)
    os.chdir('../..')

def package_debian():
    print("Packaging for Ubuntu")
    for distribution in ['trusty', 'xenial']:
        package_debian_distribution(distribution)

def package_arch():
    # For now, package_arch() will only copy the source files into build/. It copies less packages
    # than package_debian because there are more python packages available in Arch (so we don't
    # need to include them).
    print("Packaging for Arch")
    srcpath = op.join('build', 'dupeguru-arch')
    packages = [
        'hscommon', 'core', 'qtlib', 'qt', 'send2trash', 'hsaudiotag',
    ]
    copy_files_to_package(srcpath, packages, with_so=True)
    shutil.copy(op.join('images', 'dgse_logo_128.png'), srcpath)
    debopts = json.load(open(op.join('pkg', 'arch', 'dupeguru.json')))
    filereplace(op.join('pkg', 'arch', 'dupeguru.desktop'), op.join(srcpath, 'dupeguru.desktop'), **debopts)

def package_source_tgz():
    print("Creating git archive")
    app_version = get_module_version('core')
    name = 'dupeguru-src-{}.tar'.format(app_version)
    base_path = os.getcwd()
    build_path = op.join(base_path, 'build')
    dest = op.join(build_path, name)
    print_and_do('git archive -o {} HEAD'.format(dest))
    # Now, we need to include submodules
    SUBMODULES = ['hscommon', 'qtlib']
    for submodule in SUBMODULES:
        print("Adding submodule {} to archive".format(submodule))
        os.chdir(submodule)
        archive_path = op.join(build_path, '{}.tar'.format(submodule))
        print_and_do('git archive -o {} --prefix {}/ HEAD'.format(archive_path, submodule))
        os.chdir(base_path)
        print_and_do('tar -A {} -f {}'.format(archive_path, dest))
    print_and_do('gzip {}'.format(dest))

def package_windows():
    from cx_Freeze import setup, Executable
    app_version = get_module_version('core')
    arch = platform.architecture()[0]
    buildpath = op.join('build', 'dupeguru-win{}'.format(arch))
    # remove existing build directory
    if op.exists(buildpath):
        shutil.rmtree(buildpath)
    include_files = []
    # include locale files if they are built otherwise exit as it will break
    # the localization
    if op.exists('build/locale'):
        include_files.append(('build/locale', 'locale'))
    else:
        print("Locale files not built, exiting...")
        return
    # include help files if they are built otherwise exit as they should be included?
    if op.exists('build/help'):
        include_files.append(('build/help', 'help'))
    else:
        print("Help files not built, exiting...")
        return
    # options for cx_Freeze
    # if zip_include packages is not used, the cx_Freeze packager will include
    # the whole PyQT5 directory
    options = {
        'build_exe': {
            'build_exe': buildpath,
            'excludes': [],
            'includes': ['atexit', 'dbm.dumb'],
            'include_files': include_files,
            'include_msvcr': True,
            'zip_include_packages': ['*'],
            'zip_exclude_packages': []
        },
    }
    # executables to build, uses se edition icon
    executables = [
        Executable(
            script='run.py',
            base='Win32GUI',
            targetName='dupeguru.exe',
            icon='images/dgse_logo.ico',
            copyright='Copyright (C) 2017 Hardcoded Software'
        )
    ]
    # call cx_freeze
    setup(
        name='dupeguru',
        version=app_version,
        description='Tool to find duplicate files on your computer.',
        options=options,
        executables=executables,
        script_args=['build']
    )
    # Information to pass to NSIS
    version_array = app_version.split('.')
    match = re.search('[0-9]+', arch)
    bits = match.group(0)
    # Call NSIS (TODO update to not use hardcoded path)
    cmd = ('"C:\\Program Files (x86)\\NSIS\\Bin\\makensis.exe" '
           '/DVERSIONMAJOR={0} /DVERSIONMINOR={1} /DVERSIONPATCH={2} /DBITS={3} setup.nsi')
    print_and_do(cmd.format(version_array[0], version_array[1], version_array[2], bits))

def main():
    args = parse_args()
    if args.src_pkg:
        print("Creating source package for dupeGuru")
        package_source_tgz()
        return
    print("Packaging dupeGuru with UI qt")
    if sys.platform == 'win32':
        package_windows()
    else:
        if not args.arch_pkg:
            distname, _, _ = platform.dist()
        else:
            distname = 'arch'
        if distname == 'arch':
            package_arch()
        else:
            package_debian()

if __name__ == '__main__':
    main()
