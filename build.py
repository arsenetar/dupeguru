# Created By: Virgil Dupras
# Created On: 2009-12-30
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import sys
import os
import os.path as op
from optparse import OptionParser
import shutil
import json
import importlib
import compileall

from setuptools import setup, Extension

from hscommon import sphinxgen
from hscommon.build import (add_to_pythonpath, print_and_do, copy_packages, filereplace,
    get_module_version, move_all, copy_sysconfig_files_for_embed, copy_all, OSXAppStructure,
    build_cocoalib_xibless, fix_qt_resource_file, build_cocoa_ext, copy_embeddable_python_dylib,
    collect_stdlib_dependencies, copy)
from hscommon import loc
from hscommon.plat import ISOSX, ISLINUX
from hscommon.util import ensure_folder, delete_files_with_pattern

def parse_args():
    usage = "usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option('--clean', action='store_true', dest='clean',
        help="Clean build folder before building")
    parser.add_option('--doc', action='store_true', dest='doc',
        help="Build only the help file")
    parser.add_option('--loc', action='store_true', dest='loc',
        help="Build only localization")
    parser.add_option('--cocoa-ext', action='store_true', dest='cocoa_ext',
        help="Build only Cocoa extensions")
    parser.add_option('--cocoa-compile', action='store_true', dest='cocoa_compile',
        help="Build only Cocoa executable")
    parser.add_option('--xibless', action='store_true', dest='xibless',
        help="Build only xibless UIs")
    parser.add_option('--updatepot', action='store_true', dest='updatepot',
        help="Generate .pot files from source code.")
    parser.add_option('--mergepot', action='store_true', dest='mergepot',
        help="Update all .po files based on .pot files.")
    (options, args) = parser.parse_args()
    return options

def cocoa_compile_command(edition):
    return '{0} waf configure --edition {1} && {0} waf'.format(sys.executable, edition)

def cocoa_app(edition):
    app_path = {
        'se': 'build/dupeGuru.app',
        'me': 'build/dupeGuru ME.app',
        'pe': 'build/dupeGuru PE.app',
    }[edition]
    return OSXAppStructure(app_path)

def build_xibless(edition, dest='cocoa/autogen'):
    import xibless
    ensure_folder(dest)
    FNPAIRS = [
        ('ignore_list_dialog.py', 'IgnoreListDialog_UI'),
        ('deletion_options.py', 'DeletionOptions_UI'),
        ('problem_dialog.py', 'ProblemDialog_UI'),
        ('directory_panel.py', 'DirectoryPanel_UI'),
        ('prioritize_dialog.py', 'PrioritizeDialog_UI'),
        ('result_window.py', 'ResultWindow_UI'),
        ('main_menu.py', 'MainMenu_UI'),
        ('preferences_panel.py', 'PreferencesPanel_UI'),
    ]
    for srcname, dstname in FNPAIRS:
        xibless.generate(op.join('cocoa', 'base', 'ui', srcname), op.join(dest, dstname),
            localizationTable='Localizable', args={'edition': edition})
    if edition == 'pe':
        xibless.generate('cocoa/pe/ui/details_panel.py', op.join(dest, 'DetailsPanel_UI'), localizationTable='Localizable')
    else:
        xibless.generate('cocoa/base/ui/details_panel.py', op.join(dest, 'DetailsPanel_UI'), localizationTable='Localizable')

def build_cocoa(edition, dev):
    print("Creating OS X app structure")
    ed = lambda s: s.format(edition)
    app = cocoa_app(edition)
    app_version = get_module_version(ed('core_{}'))
    cocoa_project_path = ed('cocoa/{}')
    filereplace(op.join(cocoa_project_path, 'InfoTemplate.plist'), op.join('build', 'Info.plist'), version=app_version)
    app.create(op.join('build', 'Info.plist'))
    print("Building localizations")
    build_localizations('cocoa', edition)
    print("Building xibless UIs")
    build_cocoalib_xibless()
    build_xibless(edition)
    print("Building Python extensions")
    build_cocoa_proxy_module()
    build_cocoa_bridging_interfaces(edition)
    print("Building the cocoa layer")
    copy_embeddable_python_dylib('build')
    pydep_folder = op.join(app.resources, 'py')
    if not op.exists(pydep_folder):
        os.mkdir(pydep_folder)
    shutil.copy(op.join(cocoa_project_path, 'dg_cocoa.py'), 'build')
    appscript_pkgs = ['appscript', 'aem', 'mactypes']
    specific_packages = {
        'se': ['core_se'],
        'me': ['core_me'] + appscript_pkgs + ['hsaudiotag'],
        'pe': ['core_pe'] + appscript_pkgs,
    }[edition]
    tocopy = ['core', 'hscommon', 'cocoa/inter', 'cocoalib/cocoa', 'jobprogress', 'objp',
        'send2trash'] + specific_packages
    copy_packages(tocopy, pydep_folder, create_links=dev)
    sys.path.insert(0, 'build')
    extra_deps = None
    if edition == 'pe':
        # ModuleFinder can't seem to correctly detect the multiprocessing dependency, so we have
        # to manually specify it.
        extra_deps=['multiprocessing']
    collect_stdlib_dependencies('build/dg_cocoa.py', pydep_folder, extra_deps=extra_deps)
    del sys.path[0]
    # Views are not referenced by python code, so they're not found by the collector.
    copy_all('build/inter/*.so', op.join(pydep_folder, 'inter'))
    copy_sysconfig_files_for_embed(pydep_folder)
    if not dev:
        # Important: Don't ever run delete_files_with_pattern('*.py') on dev builds because you'll
        # be deleting all py files in symlinked folders.
        compileall.compile_dir(pydep_folder, force=True, legacy=True)
        delete_files_with_pattern(pydep_folder, '*.py')
        delete_files_with_pattern(pydep_folder, '__pycache__')
    print("Compiling with WAF")
    os.chdir('cocoa')
    print_and_do(cocoa_compile_command(edition))
    os.chdir('..')
    app.copy_executable('cocoa/build/dupeGuru')
    print("Copying resources and frameworks")
    image_path = ed('cocoa/{}/dupeguru.icns')
    resources = [image_path, 'cocoa/base/dsa_pub.pem', 'build/dg_cocoa.py', 'build/help']
    app.copy_resources(*resources, use_symlinks=dev)
    app.copy_frameworks('build/Python', 'cocoalib/Sparkle.framework')
    print("Creating the run.py file")
    tmpl = open('cocoa/run_template.py', 'rt').read()
    run_contents = tmpl.replace('{{app_path}}', app.dest)
    open('run.py', 'wt').write(run_contents)

def build_qt(edition, dev, conf):
    print("Building localizations")
    build_localizations('qt', edition)
    print("Building Qt stuff")
    print_and_do("pyrcc4 -py3 {0} > {1}".format(op.join('qt', 'base', 'dg.qrc'), op.join('qt', 'base', 'dg_rc.py')))
    fix_qt_resource_file(op.join('qt', 'base', 'dg_rc.py'))
    print("Creating the run.py file")
    filereplace(op.join('qt', 'run_template.py'), 'run.py', edition=edition)

def build_help(edition):
    print("Generating Help")
    current_path = op.abspath('.')
    help_basepath = op.join(current_path, 'help', 'en')
    help_destpath = op.join(current_path, 'build', 'help'.format(edition))
    changelog_path = op.join(current_path, 'help', 'changelog_{}'.format(edition))
    tixurl = "https://github.com/hsoft/dupeguru/issues/{}"
    appname = {'se': 'dupeGuru', 'me': 'dupeGuru Music Edition', 'pe': 'dupeGuru Picture Edition'}[edition]
    homepage = 'http://www.hardcoded.net/dupeguru{}/'.format('_' + edition if edition != 'se' else '')
    confrepl = {'edition': edition, 'appname': appname, 'homepage': homepage, 'language': 'en'}
    changelogtmpl = op.join(current_path, 'help', 'changelog.tmpl')
    conftmpl = op.join(current_path, 'help', 'conf.tmpl')
    sphinxgen.gen(help_basepath, help_destpath, changelog_path, tixurl, confrepl, conftmpl, changelogtmpl)

def build_base_localizations():
    loc.compile_all_po('locale')
    loc.compile_all_po(op.join('hscommon', 'locale'))
    loc.merge_locale_dir(op.join('hscommon', 'locale'), 'locale')

def build_qt_localizations():
    loc.compile_all_po(op.join('qtlib', 'locale'))
    loc.merge_locale_dir(op.join('qtlib', 'locale'), 'locale')

def build_localizations(ui, edition):
    build_base_localizations()
    if ui == 'cocoa':
        app = cocoa_app(edition)
        loc.build_cocoa_localizations(app, en_stringsfile=op.join('cocoa', 'base', 'en.lproj', 'Localizable.strings'))
        locale_dest = op.join(app.resources, 'locale')
    elif ui == 'qt':
        build_qt_localizations()
        locale_dest = op.join('build', 'locale')
    if op.exists(locale_dest):
        shutil.rmtree(locale_dest)
    shutil.copytree('locale', locale_dest, ignore=shutil.ignore_patterns('*.po', '*.pot'))
    if ui == 'qt' and not ISLINUX:
        print("Copying qt_*.qm files into the 'locale' folder")
        from PyQt4.QtCore import QLibraryInfo
        trfolder = QLibraryInfo.location(QLibraryInfo.TranslationsPath)
        for lang in loc.get_langs('locale'):
            qmname = 'qt_%s.qm' % lang
            src = op.join(trfolder, qmname)
            if op.exists(src):
                copy(src, op.join('build', 'locale', qmname))

def build_updatepot():
    if ISOSX:
        print("Updating Cocoa strings file.")
        # We need to have strings from *all* editions in here, so we'll call xibless for all editions
        # in dummy subfolders.
        build_cocoalib_xibless('cocoalib/autogen')
        loc.generate_cocoa_strings_from_code('cocoalib', 'cocoalib/en.lproj')
        for edition in ('se', 'me', 'pe'):
            build_xibless(edition, op.join('cocoa', 'autogen', edition))
        loc.generate_cocoa_strings_from_code('cocoa', 'cocoa/base/en.lproj')
    print("Building .pot files from source files")
    print("Building core.pot")
    all_cores = ['core', 'core_se', 'core_me', 'core_pe']
    loc.generate_pot(all_cores, op.join('locale', 'core.pot'), ['tr'])
    print("Building columns.pot")
    loc.generate_pot(all_cores, op.join('locale', 'columns.pot'), ['coltr'])
    print("Building ui.pot")
    # When we're not under OS X, we don't want to overwrite ui.pot because it contains Cocoa locs
    # We want to merge the generated pot with the old pot in the most preserving way possible.
    ui_packages = ['qt', op.join('cocoa', 'inter')]
    loc.generate_pot(ui_packages, op.join('locale', 'ui.pot'), ['tr'], merge=(not ISOSX))
    print("Building hscommon.pot")
    loc.generate_pot(['hscommon'], op.join('hscommon', 'locale', 'hscommon.pot'), ['tr'])
    print("Building qtlib.pot")
    loc.generate_pot(['qtlib'], op.join('qtlib', 'locale', 'qtlib.pot'), ['tr'])
    if ISOSX:
        print("Building cocoalib.pot")
        cocoalib_pot = op.join('cocoalib', 'locale', 'cocoalib.pot')
        os.remove(cocoalib_pot)
        loc.strings2pot(op.join('cocoalib', 'en.lproj', 'cocoalib.strings'), cocoalib_pot)
        print("Enhancing ui.pot with Cocoa's strings files")
        loc.strings2pot(op.join('cocoa', 'base', 'en.lproj', 'Localizable.strings'),
            op.join('locale', 'ui.pot'))

def build_mergepot():
    print("Updating .po files using .pot files")
    loc.merge_pots_into_pos('locale')
    loc.merge_pots_into_pos(op.join('hscommon', 'locale'))
    loc.merge_pots_into_pos(op.join('qtlib', 'locale'))
    loc.merge_pots_into_pos(op.join('cocoalib', 'locale'))

def build_cocoa_proxy_module():
    print("Building Cocoa Proxy")
    import objp.p2o
    objp.p2o.generate_python_proxy_code('cocoalib/cocoa/CocoaProxy.h', 'build/CocoaProxy.m')
    build_cocoa_ext("CocoaProxy", 'cocoalib/cocoa',
        ['cocoalib/cocoa/CocoaProxy.m', 'build/CocoaProxy.m', 'build/ObjP.m',
            'cocoalib/HSErrorReportWindow.m', 'cocoa/autogen/HSErrorReportWindow_UI.m'],
        ['AppKit', 'CoreServices'],
        ['cocoalib', 'cocoa/autogen'])

def build_cocoa_bridging_interfaces(edition):
    print("Building Cocoa Bridging Interfaces")
    import objp.o2p
    import objp.p2o
    add_to_pythonpath('cocoa')
    add_to_pythonpath('cocoalib')
    from cocoa.inter import (PyGUIObject, GUIObjectView, PyColumns, ColumnsView, PyOutline,
        OutlineView, PySelectableList, SelectableListView, PyTable, TableView, PyBaseApp,
        PyFairware, PyTextField, ProgressWindowView, PyProgressWindow)
    from inter.deletion_options import PyDeletionOptions, DeletionOptionsView
    from inter.details_panel import PyDetailsPanel, DetailsPanelView
    from inter.directory_outline import PyDirectoryOutline, DirectoryOutlineView
    from inter.prioritize_dialog import PyPrioritizeDialog, PrioritizeDialogView
    from inter.prioritize_list import PyPrioritizeList, PrioritizeListView
    from inter.problem_dialog import PyProblemDialog
    from inter.ignore_list_dialog import PyIgnoreListDialog, IgnoreListDialogView
    from inter.result_table import PyResultTable, ResultTableView
    from inter.stats_label import PyStatsLabel, StatsLabelView
    from inter.app import PyDupeGuruBase, DupeGuruView
    appmod = importlib.import_module('inter.app_{}'.format(edition))
    allclasses = [PyGUIObject, PyColumns, PyOutline, PySelectableList, PyTable, PyBaseApp, PyFairware,
        PyDetailsPanel, PyDirectoryOutline, PyPrioritizeDialog, PyPrioritizeList, PyProblemDialog,
        PyIgnoreListDialog, PyDeletionOptions, PyResultTable, PyStatsLabel, PyDupeGuruBase,
        PyTextField, PyProgressWindow, appmod.PyDupeGuru]
    for class_ in allclasses:
        objp.o2p.generate_objc_code(class_, 'cocoa/autogen', inherit=True)
    allclasses = [GUIObjectView, ColumnsView, OutlineView, SelectableListView, TableView,
        DetailsPanelView, DirectoryOutlineView, PrioritizeDialogView, PrioritizeListView,
        IgnoreListDialogView, DeletionOptionsView, ResultTableView, StatsLabelView,
        ProgressWindowView, DupeGuruView]
    clsspecs = [objp.o2p.spec_from_python_class(class_) for class_ in allclasses]
    objp.p2o.generate_python_proxy_code_from_clsspec(clsspecs, 'build/CocoaViews.m')
    build_cocoa_ext('CocoaViews', 'cocoa/inter', ['build/CocoaViews.m', 'build/ObjP.m'])

def build_pe_modules(ui):
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
    move_all('_block_qt*', op.join('qt', 'pe'))
    move_all('_block*', 'core_pe')
    move_all('_cache*', 'core_pe')

def build_normal(edition, ui, dev, conf):
    print("Building dupeGuru {0} with UI {1}".format(edition.upper(), ui))
    add_to_pythonpath('.')
    build_help(edition)
    print("Building dupeGuru")
    if edition == 'pe':
        build_pe_modules(ui)
    if ui == 'cocoa':
        build_cocoa(edition, dev)
    elif ui == 'qt':
        build_qt(edition, dev, conf)

def main():
    options = parse_args()
    conf = json.load(open('conf.json'))
    edition = conf['edition']
    ui = conf['ui']
    dev = conf['dev']
    if dev:
        print("Building in Dev mode")
    if options.clean:
        if op.exists('build'):
            shutil.rmtree('build')
    if not op.exists('build'):
        os.mkdir('build')
    if options.doc:
        build_help(edition)
    elif options.loc:
        build_localizations(ui, edition)
    elif options.updatepot:
        build_updatepot()
    elif options.mergepot:
        build_mergepot()
    elif options.cocoa_ext:
        build_cocoa_proxy_module()
        build_cocoa_bridging_interfaces(edition)
    elif options.cocoa_compile:
        os.chdir('cocoa')
        print_and_do(cocoa_compile_command(edition))
        os.chdir('..')
        cocoa_app(edition).copy_executable('cocoa/build/dupeGuru')
    elif options.xibless:
        build_cocoalib_xibless()
        build_xibless(edition)
    else:
        build_normal(edition, ui, dev, conf)

if __name__ == '__main__':
    main()
