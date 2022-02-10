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
import distro
import re

from hscommon.build import (
    print_and_do,
    copy_packages,
    build_debian_changelog,
    get_module_version,
    filereplace,
    copy,
    setup_package_argparser,
    copy_all,
)

ENTRY_SCRIPT = "run.py"
LOCALE_DIR = "build/locale"
HELP_DIR = "build/help"


def parse_args():
    parser = ArgumentParser()
    setup_package_argparser(parser)
    return parser.parse_args()


def check_loc_doc():
    if not op.exists(LOCALE_DIR):
        print('Locale files are missing. Have you run "build.py --loc"?')
    # include help files if they are built otherwise exit as they should be included?
    if not op.exists(HELP_DIR):
        print('Help files are missing. Have you run "build.py --doc"?')
    return op.exists(LOCALE_DIR) and op.exists(HELP_DIR)


def copy_files_to_package(destpath, packages, with_so):
    # when with_so is true, we keep .so files in the package, and otherwise, we don't. We need this
    # flag because when building debian src pkg, we *don't* want .so files (they're compiled later)
    # and when we're packaging under Arch, we're packaging a binary package, so we want them.
    if op.exists(destpath):
        shutil.rmtree(destpath)
    os.makedirs(destpath)
    shutil.copy(ENTRY_SCRIPT, op.join(destpath, ENTRY_SCRIPT))
    extra_ignores = ["*.so"] if not with_so else None
    copy_packages(packages, destpath, extra_ignores=extra_ignores)
    # include locale files if they are built otherwise exit as it will break
    # the localization
    if not check_loc_doc():
        print("Exiting...")
        return
    shutil.copytree(op.join("build", "help"), op.join(destpath, "help"))
    shutil.copytree(op.join("build", "locale"), op.join(destpath, "locale"))
    compileall.compile_dir(destpath)


def package_debian_distribution(distribution):
    app_version = get_module_version("core")
    version = "{}~{}".format(app_version, distribution)
    destpath = op.join("build", "dupeguru-{}".format(version))
    srcpath = op.join(destpath, "src")
    packages = ["hscommon", "core", "qtlib", "qt", "send2trash"]
    copy_files_to_package(srcpath, packages, with_so=False)
    os.mkdir(op.join(destpath, "modules"))
    copy_all(op.join("core", "pe", "modules", "*.*"), op.join(destpath, "modules"))
    copy(
        op.join("qt", "pe", "modules", "block.c"),
        op.join(destpath, "modules", "block_qt.c"),
    )
    copy(
        op.join("pkg", "debian", "build_pe_modules.py"),
        op.join(destpath, "build_pe_modules.py"),
    )
    debdest = op.join(destpath, "debian")
    debskel = op.join("pkg", "debian")
    os.makedirs(debdest)
    debopts = json.load(open(op.join(debskel, "dupeguru.json")))
    for fn in ["compat", "copyright", "dirs", "rules", "source"]:
        copy(op.join(debskel, fn), op.join(debdest, fn))
    filereplace(op.join(debskel, "control"), op.join(debdest, "control"), **debopts)
    filereplace(op.join(debskel, "Makefile"), op.join(destpath, "Makefile"), **debopts)
    filereplace(op.join(debskel, "dupeguru.desktop"), op.join(debdest, "dupeguru.desktop"), **debopts)
    changelogpath = op.join("help", "changelog")
    changelog_dest = op.join(debdest, "changelog")
    project_name = debopts["pkgname"]
    from_version = "2.9.2"
    build_debian_changelog(
        changelogpath,
        changelog_dest,
        project_name,
        from_version=from_version,
        distribution=distribution,
    )
    shutil.copy(op.join("images", "dgse_logo_128.png"), srcpath)
    os.chdir(destpath)
    cmd = "dpkg-buildpackage -F -us -uc"
    os.system(cmd)
    os.chdir("../..")


def package_debian():
    print("Packaging for Debian/Ubuntu")
    for distribution in ["unstable"]:
        package_debian_distribution(distribution)


def package_arch():
    # For now, package_arch() will only copy the source files into build/. It copies less packages
    # than package_debian because there are more python packages available in Arch (so we don't
    # need to include them).
    print("Packaging for Arch")
    srcpath = op.join("build", "dupeguru-arch")
    packages = ["hscommon", "core", "qtlib", "qt", "send2trash"]
    copy_files_to_package(srcpath, packages, with_so=True)
    shutil.copy(op.join("images", "dgse_logo_128.png"), srcpath)
    debopts = json.load(open(op.join("pkg", "arch", "dupeguru.json")))
    filereplace(op.join("pkg", "arch", "dupeguru.desktop"), op.join(srcpath, "dupeguru.desktop"), **debopts)


def package_source_txz():
    print("Creating git archive")
    app_version = get_module_version("core")
    name = "dupeguru-src-{}.tar".format(app_version)
    base_path = os.getcwd()
    build_path = op.join(base_path, "build")
    dest = op.join(build_path, name)
    print_and_do("git archive -o {} HEAD".format(dest))
    print_and_do("xz {}".format(dest))


def package_windows():
    app_version = get_module_version("core")
    arch = platform.architecture()[0]
    # Information to pass to pyinstaller and NSIS
    match = re.search("[0-9]+.[0-9]+.[0-9]+", app_version)
    version_array = match.group(0).split(".")
    match = re.search("[0-9]+", arch)
    bits = match.group(0)
    if bits == "64":
        arch = "x64"
    else:
        arch = "x86"
    # include locale files if they are built otherwise exit as it will break
    # the localization
    if not check_loc_doc():
        print("Exiting...")
        return
    # create version information file from template
    try:
        version_template = open("win_version_info.temp", "r")
        version_info = version_template.read()
        version_template.close()
        version_info_file = open("win_version_info.txt", "w")
        version_info_file.write(version_info.format(version_array[0], version_array[1], version_array[2], bits))
        version_info_file.close()
    except Exception:
        print("Error creating version info file, exiting...")
        return
    # run pyinstaller from here:
    import PyInstaller.__main__

    # UCRT dlls are included if the system has the windows kit installed
    PyInstaller.__main__.run(
        [
            "--name=dupeguru-win{0}".format(bits),
            "--windowed",
            "--noconfirm",
            "--icon=images/dgse_logo.ico",
            "--add-data={0};locale".format(LOCALE_DIR),
            "--add-data={0};help".format(HELP_DIR),
            "--version-file=win_version_info.txt",
            "--paths=C:\\Program Files (x86)\\Windows Kits\\10\\Redist\\ucrt\\DLLs\\{0}".format(arch),
            ENTRY_SCRIPT,
        ]
    )
    # remove version info file
    os.remove("win_version_info.txt")
    # Call NSIS (TODO update to not use hardcoded path)
    cmd = (
        '"C:\\Program Files (x86)\\NSIS\\Bin\\makensis.exe" '
        "/DVERSIONMAJOR={0} /DVERSIONMINOR={1} /DVERSIONPATCH={2} /DBITS={3} setup.nsi"
    )
    print_and_do(cmd.format(version_array[0], version_array[1], version_array[2], bits))


def package_macos():
    # include locale files if they are built otherwise exit as it will break
    # the localization
    if not check_loc_doc():
        print("Exiting")
        return
    # run pyinstaller from here:
    import PyInstaller.__main__

    PyInstaller.__main__.run(
        [
            "--name=dupeguru",
            "--windowed",
            "--noconfirm",
            "--icon=images/dupeguru.icns",
            "--osx-bundle-identifier=com.hardcoded-software.dupeguru",
            "--add-data={0}:locale".format(LOCALE_DIR),
            "--add-data={0}:help".format(HELP_DIR),
            "{0}".format(ENTRY_SCRIPT),
        ]
    )


def main():
    args = parse_args()
    if args.src_pkg:
        print("Creating source package for dupeGuru")
        package_source_txz()
        return
    print("Packaging dupeGuru with UI qt")
    if sys.platform == "win32":
        package_windows()
    elif sys.platform == "darwin":
        package_macos()
    else:
        if not args.arch_pkg:
            distname = distro.id()
        else:
            distname = "arch"
        if distname == "arch":
            package_arch()
        else:
            package_debian()


if __name__ == "__main__":
    main()
