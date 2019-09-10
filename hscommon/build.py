# Created By: Virgil Dupras
# Created On: 2009-03-03
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

"""This module is a collection of function to help in HS apps build process.
"""

import os
import sys
import os.path as op
import shutil
import tempfile
import plistlib
from subprocess import Popen
import re
import importlib
from datetime import datetime
import glob
import sysconfig
import modulefinder

from setuptools import setup, Extension

from .plat import ISWINDOWS
from .util import modified_after, find_in_path, ensure_folder, delete_files_with_pattern

def print_and_do(cmd):
    """Prints ``cmd`` and executes it in the shell.
    """
    print(cmd)
    p = Popen(cmd, shell=True)
    return p.wait()

def _perform(src, dst, action, actionname):
    if not op.lexists(src):
        print("Copying %s failed: it doesn't exist." % src)
        return
    if op.lexists(dst):
        if op.isdir(dst):
            shutil.rmtree(dst)
        else:
            os.remove(dst)
    print('%s %s --> %s' % (actionname, src, dst))
    action(src, dst)

def copy_file_or_folder(src, dst):
    if op.isdir(src):
        shutil.copytree(src, dst, symlinks=True)
    else:
        shutil.copy(src, dst)

def move(src, dst):
    _perform(src, dst, os.rename, 'Moving')

def copy(src, dst):
    _perform(src, dst, copy_file_or_folder, 'Copying')

def symlink(src, dst):
    _perform(src, dst, os.symlink, 'Symlinking')

def hardlink(src, dst):
    _perform(src, dst, os.link, 'Hardlinking')

def _perform_on_all(pattern, dst, action):
    # pattern is a glob pattern, example "folder/foo*". The file is moved directly in dst, no folder
    # structure from src is kept.
    filenames = glob.glob(pattern)
    for fn in filenames:
        destpath = op.join(dst, op.basename(fn))
        action(fn, destpath)

def move_all(pattern, dst):
    _perform_on_all(pattern, dst, move)

def copy_all(pattern, dst):
    _perform_on_all(pattern, dst, copy)

def ensure_empty_folder(path):
    """Make sure that the path exists and that it's an empty folder.
    """
    if op.exists(path):
        shutil.rmtree(path)
    os.mkdir(path)

def filereplace(filename, outfilename=None, **kwargs):
    """Reads `filename`, replaces all {variables} in kwargs, and writes the result to `outfilename`.
    """
    if outfilename is None:
        outfilename = filename
    fp = open(filename, 'rt', encoding='utf-8')
    contents = fp.read()
    fp.close()
    # We can't use str.format() because in some files, there might be {} characters that mess with it.
    for key, item in kwargs.items():
        contents = contents.replace('{{{}}}'.format(key), item)
    fp = open(outfilename, 'wt', encoding='utf-8')
    fp.write(contents)
    fp.close()

def get_module_version(modulename):
    mod = importlib.import_module(modulename)
    return mod.__version__

def setup_package_argparser(parser):
    parser.add_argument(
        '--sign', dest='sign_identity',
        help="Sign app under specified identity before packaging (OS X only)"
    )
    parser.add_argument(
        '--nosign', action='store_true', dest='nosign',
        help="Don't sign the packaged app (OS X only)"
    )
    parser.add_argument(
        '--src-pkg', action='store_true', dest='src_pkg',
        help="Build a tar.gz of the current source."
    )
    parser.add_argument(
        '--arch-pkg', action='store_true', dest='arch_pkg',
        help="Force Arch Linux packaging type, regardless of distro name."
    )

# `args` come from an ArgumentParser updated with setup_package_argparser()
def package_cocoa_app_in_dmg(app_path, destfolder, args):
    # Rather than signing our app in XCode during the build phase, we sign it during the package
    # phase because running the app before packaging can modify it and we want to be sure to have
    # a valid signature.
    if args.sign_identity:
        sign_identity = "Developer ID Application: {}".format(args.sign_identity)
        result = print_and_do('codesign --force --deep --sign "{}" "{}"'.format(sign_identity, app_path))
        if result != 0:
            print("ERROR: Signing failed. Aborting packaging.")
            return
    elif not args.nosign:
        print("ERROR: Either --nosign or --sign argument required.")
        return
    build_dmg(app_path, destfolder)

def build_dmg(app_path, destfolder):
    """Builds a DMG volume with application at ``app_path`` and puts it in ``dest_path``.

    The name of the resulting DMG volume is determined by the app's name and version.
    """
    print(repr(op.join(app_path, 'Contents', 'Info.plist')))
    plist = plistlib.readPlist(op.join(app_path, 'Contents', 'Info.plist'))
    workpath = tempfile.mkdtemp()
    dmgpath = op.join(workpath, plist['CFBundleName'])
    os.mkdir(dmgpath)
    print_and_do('cp -R "%s" "%s"' % (app_path, dmgpath))
    print_and_do('ln -s /Applications "%s"' % op.join(dmgpath, 'Applications'))
    dmgname = '%s_osx_%s.dmg' % (plist['CFBundleName'].lower().replace(' ', '_'), plist['CFBundleVersion'].replace('.', '_'))
    print('Building %s' % dmgname)
    # UDBZ = bzip compression. UDZO (zip compression) was used before, but it compresses much less.
    print_and_do('hdiutil create "%s" -format UDBZ -nocrossdev -srcdir "%s"' % (op.join(destfolder, dmgname), dmgpath))
    print('Build Complete')

def copy_sysconfig_files_for_embed(destpath):
    # This normally shouldn't be needed for Python 3.3+.
    makefile = sysconfig.get_makefile_filename()
    configh = sysconfig.get_config_h_filename()
    shutil.copy(makefile, destpath)
    shutil.copy(configh, destpath)
    with open(op.join(destpath, 'site.py'), 'w') as fp:
        fp.write("""
import os.path as op
from distutils import sysconfig
sysconfig.get_makefile_filename = lambda: op.join(op.dirname(__file__), 'Makefile')
sysconfig.get_config_h_filename = lambda: op.join(op.dirname(__file__), 'pyconfig.h')
""")

def add_to_pythonpath(path):
    """Adds ``path`` to both ``PYTHONPATH`` env and ``sys.path``.
    """
    abspath = op.abspath(path)
    pythonpath = os.environ.get('PYTHONPATH', '')
    pathsep = ';' if ISWINDOWS else ':'
    pythonpath = pathsep.join([abspath, pythonpath]) if pythonpath else abspath
    os.environ['PYTHONPATH'] = pythonpath
    sys.path.insert(1, abspath)

# This is a method to hack around those freakingly tricky data inclusion/exlusion rules
# in setuptools. We copy the packages *without data* in a build folder and then build the plugin
# from there.
def copy_packages(packages_names, dest, create_links=False, extra_ignores=None):
    """Copy python packages ``packages_names`` to ``dest``, spurious data.

    Copy will happen without tests, testdata, mercurial data or C extension module source with it.
    ``py2app`` include and exclude rules are **quite** funky, and doing this is the only reliable
    way to make sure we don't end up with useless stuff in our app.
    """
    if ISWINDOWS:
        create_links = False
    if not extra_ignores:
        extra_ignores = []
    ignore = shutil.ignore_patterns('.hg*', 'tests', 'testdata', 'modules', 'docs', 'locale', *extra_ignores)
    for package_name in packages_names:
        if op.exists(package_name):
            source_path = package_name
        else:
            mod = __import__(package_name)
            source_path = mod.__file__
            if mod.__file__.endswith('__init__.py'):
                source_path = op.dirname(source_path)
        dest_name = op.basename(source_path)
        dest_path = op.join(dest, dest_name)
        if op.exists(dest_path):
            if op.islink(dest_path):
                os.unlink(dest_path)
            else:
                shutil.rmtree(dest_path)
        print("Copying package at {0} to {1}".format(source_path, dest_path))
        if create_links:
            os.symlink(op.abspath(source_path), dest_path)
        else:
            if op.isdir(source_path):
                shutil.copytree(source_path, dest_path, ignore=ignore)
            else:
                shutil.copy(source_path, dest_path)

def copy_qt_plugins(folder_names, dest): # This is only for Windows
    from PyQt5.QtCore import QLibraryInfo
    qt_plugin_dir = QLibraryInfo.location(QLibraryInfo.PluginsPath)
    def ignore(path, names):
        if path == qt_plugin_dir:
            return [n for n in names if n not in folder_names]
        else:
            return [n for n in names if not n.endswith('.dll')]
    shutil.copytree(qt_plugin_dir, dest, ignore=ignore)

def build_debian_changelog(changelogpath, destfile, pkgname, from_version=None,
        distribution='precise', fix_version=None):
    """Builds a debian changelog out of a YAML changelog.

    Use fix_version to patch the top changelog to that version (if, for example, there was a
    packaging error and you need to quickly fix it)
    """
    def desc2list(desc):
        # We take each item, enumerated with the '*' character, and transform it into a list.
        desc = desc.replace('\n', ' ')
        desc = desc.replace('  ', ' ')
        result = desc.split('*')
        return [s.strip() for s in result if s.strip()]

    ENTRY_MODEL = "{pkg} ({version}~{distribution}) {distribution}; urgency=low\n\n{changes}\n -- Virgil Dupras <hsoft@hardcoded.net>  {date}\n\n"
    CHANGE_MODEL = "  * {description}\n"
    changelogs = read_changelog_file(changelogpath)
    if from_version:
        # We only want logs from a particular version
        for index, log in enumerate(changelogs):
            if log['version'] == from_version:
                changelogs = changelogs[:index+1]
                break
    if fix_version:
        changelogs[0]['version'] = fix_version
    rendered_logs = []
    for log in changelogs:
        version = log['version']
        logdate = log['date']
        desc = log['description']
        rendered_date = logdate.strftime('%a, %d %b %Y 00:00:00 +0000')
        rendered_descs = [CHANGE_MODEL.format(description=d) for d in desc2list(desc)]
        changes = ''.join(rendered_descs)
        rendered_log = ENTRY_MODEL.format(pkg=pkgname, version=version, changes=changes,
            date=rendered_date, distribution=distribution)
        rendered_logs.append(rendered_log)
    result = ''.join(rendered_logs)
    fp = open(destfile, 'w')
    fp.write(result)
    fp.close()

re_changelog_header = re.compile(r'=== ([\d.b]*) \(([\d\-]*)\)')
def read_changelog_file(filename):
    def iter_by_three(it):
        while True:
            try:
                version = next(it)
                date = next(it)
                description = next(it)
            except StopIteration:
                return
            yield version, date, description

    with open(filename, 'rt', encoding='utf-8') as fp:
        contents = fp.read()
    splitted = re_changelog_header.split(contents)[1:] # the first item is empty
    # splitted = [version1, date1, desc1, version2, date2, ...]
    result = []
    for version, date_str, description in iter_by_three(iter(splitted)):
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        d = {'date': date, 'date_str': date_str, 'version': version, 'description': description.strip()}
        result.append(d)
    return result

class OSXAppStructure:
    def __init__(self, dest):
        self.dest = dest
        self.contents = op.join(dest, 'Contents')
        self.macos = op.join(self.contents, 'MacOS')
        self.resources = op.join(self.contents, 'Resources')
        self.frameworks = op.join(self.contents, 'Frameworks')
        self.infoplist = op.join(self.contents, 'Info.plist')

    def create(self, infoplist):
        ensure_empty_folder(self.dest)
        os.makedirs(self.macos)
        os.mkdir(self.resources)
        os.mkdir(self.frameworks)
        copy(infoplist, self.infoplist)
        open(op.join(self.contents, 'PkgInfo'), 'wt').write("APPLxxxx")

    def copy_executable(self, executable):
        info = plistlib.readPlist(self.infoplist)
        self.executablename = info['CFBundleExecutable']
        self.executablepath = op.join(self.macos, self.executablename)
        copy(executable, self.executablepath)

    def copy_resources(self, *resources, use_symlinks=False):
        for path in resources:
            resource_dest = op.join(self.resources, op.basename(path))
            action = symlink if use_symlinks else copy
            action(op.abspath(path), resource_dest)

    def copy_frameworks(self, *frameworks):
        for path in frameworks:
            framework_dest = op.join(self.frameworks, op.basename(path))
            copy(path, framework_dest)


def create_osx_app_structure(dest, executable, infoplist, resources=None, frameworks=None,
        symlink_resources=False):
    # `dest`: A path to the destination .app folder
    # `executable`: the path of the executable file that goes in "MacOS"
    # `infoplist`: The path to your Info.plist file.
    # `resources`: A list of paths of files or folders going in the "Resources" folder.
    # `frameworks`: Same as above for "Frameworks".
    # `symlink_resources`: If True, will symlink resources into the structure instead of copying them.
    app = OSXAppStructure(dest, infoplist)
    app.create()
    app.copy_executable(executable)
    app.copy_resources(*resources, use_symlinks=symlink_resources)
    app.copy_frameworks(*frameworks)

class OSXFrameworkStructure:
    def __init__(self, dest):
        self.dest = dest
        self.contents = op.join(dest, 'Versions', 'A')
        self.resources = op.join(self.contents, 'Resources')
        self.headers = op.join(self.contents, 'Headers')
        self.infoplist = op.join(self.resources, 'Info.plist')
        self._update_executable_path()

    def _update_executable_path(self):
        if not op.exists(self.infoplist):
            self.executablename = self.executablepath = None
            return
        info = plistlib.readPlist(self.infoplist)
        self.executablename = info['CFBundleExecutable']
        self.executablepath = op.join(self.contents, self.executablename)

    def create(self, infoplist):
        ensure_empty_folder(self.dest)
        os.makedirs(self.contents)
        os.mkdir(self.resources)
        os.mkdir(self.headers)
        copy(infoplist, self.infoplist)
        self._update_executable_path()

    def create_symlinks(self):
        # Only call this after create() and copy_executable()
        rel = lambda path: op.relpath(path, self.dest)
        os.symlink('A', op.join(self.dest, 'Versions', 'Current'))
        os.symlink(rel(self.executablepath), op.join(self.dest, self.executablename))
        os.symlink(rel(self.headers), op.join(self.dest, 'Headers'))
        os.symlink(rel(self.resources), op.join(self.dest, 'Resources'))

    def copy_executable(self, executable):
        copy(executable, self.executablepath)

    def copy_resources(self, *resources, use_symlinks=False):
        for path in resources:
            resource_dest = op.join(self.resources, op.basename(path))
            action = symlink if use_symlinks else copy
            action(op.abspath(path), resource_dest)

    def copy_headers(self, *headers, use_symlinks=False):
        for path in headers:
            header_dest = op.join(self.headers, op.basename(path))
            action = symlink if use_symlinks else copy
            action(op.abspath(path), header_dest)


def copy_embeddable_python_dylib(dst):
    runtime = op.join(sysconfig.get_config_var('PYTHONFRAMEWORKPREFIX'), sysconfig.get_config_var('LDLIBRARY'))
    filedest = op.join(dst, 'Python')
    shutil.copy(runtime, filedest)
    os.chmod(filedest, 0o774) # We need write permission to use install_name_tool
    cmd = 'install_name_tool -id @rpath/Python %s' % filedest
    print_and_do(cmd)

def collect_stdlib_dependencies(script, dest_folder, extra_deps=None):
    sysprefix = sys.prefix # could be a virtualenv
    real_lib_prefix = sysconfig.get_config_var('LIBDEST')
    def is_stdlib_path(path):
        # A module path is only a stdlib path if it's in either sys.prefix or
        # sysconfig.get_config_var('prefix') (the 2 are different if we are in a virtualenv) and if
        # there's no "site-package in the path.
        if not path:
            return False
        if 'site-package' in path:
            return False
        if not (path.startswith(sysprefix) or path.startswith(real_lib_prefix)):
            return False
        return True

    ensure_folder(dest_folder)
    mf = modulefinder.ModuleFinder()
    mf.run_script(script)
    modpaths = [mod.__file__ for mod in mf.modules.values()]
    modpaths = filter(is_stdlib_path, modpaths)
    for p in modpaths:
        if p.startswith(real_lib_prefix):
            relpath = op.relpath(p, real_lib_prefix)
        elif p.startswith(sysprefix):
            relpath = op.relpath(p, sysprefix)
            assert relpath.startswith('lib/python3.') # we want to get rid of that lib/python3.x part
            relpath = relpath[len('lib/python3.X/'):]
        else:
            raise AssertionError()
        if relpath.startswith('lib-dynload'): # We copy .so files in lib-dynload directly in our dest
            relpath = relpath[len('lib-dynload/'):]
        if relpath.startswith('encodings') or relpath.startswith('distutils'):
            # We force their inclusion later.
            continue
        dest_path = op.join(dest_folder, relpath)
        ensure_folder(op.dirname(dest_path))
        copy(p, dest_path)
    # stringprep is used by encodings.
    # We use real_lib_prefix with distutils because virtualenv messes with it and we need to refer
    # to the original distutils folder.
    FORCED_INCLUSION = ['encodings', 'stringprep', op.join(real_lib_prefix, 'distutils')]
    if extra_deps:
        FORCED_INCLUSION += extra_deps
    copy_packages(FORCED_INCLUSION, dest_folder)
    # There's a couple of rather big exe files in the distutils folder that we absolutely don't
    # need. Remove them.
    delete_files_with_pattern(op.join(dest_folder, 'distutils'), '*.exe')
    # And, finally, create an empty "site.py" that Python needs around on startup.
    open(op.join(dest_folder, 'site.py'), 'w').close()

def fix_qt_resource_file(path):
    # pyrcc5 under Windows, if the locale is non-english, can produce a source file with a date
    # containing accented characters. If it does, the encoding is wrong and it prevents the file
    # from being correctly frozen by cx_freeze. To work around that, we open the file, strip all
    # comments, and save.
    with open(path, 'rb') as fp:
        contents = fp.read()
    lines = contents.split(b'\n')
    lines = [l for l in lines if not l.startswith(b'#')]
    with open(path, 'wb') as fp:
        fp.write(b'\n'.join(lines))

def build_cocoa_ext(extname, dest, source_files, extra_frameworks=(), extra_includes=()):
    extra_link_args = ["-framework", "CoreFoundation", "-framework", "Foundation"]
    for extra in extra_frameworks:
        extra_link_args += ['-framework', extra]
    ext = Extension(extname, source_files, extra_link_args=extra_link_args, include_dirs=extra_includes)
    setup(script_args=['build_ext', '--inplace'], ext_modules=[ext])
    # Our problem here is to get the fully qualified filename of the resulting .so but I couldn't
    # find a documented way to do so. The only thing I could find is this below :(
    fn = ext._file_name
    assert op.exists(fn)
    move(fn, op.join(dest, fn))
