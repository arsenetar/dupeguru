# Created By: Virgil Dupras
# Created On: 2009-12-30
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
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

from setuptools import setup, Extension

from hscommon import sphinxgen
from hscommon.build import (add_to_pythonpath, print_and_do, copy_packages, filereplace,
    get_module_version, build_all_cocoa_locs, move_all, copy_sysconfig_files_for_embed, copy_all,
    move)
from hscommon import loc

def parse_args():
    usage = "usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option('--clean', action='store_true', dest='clean',
        help="Clean build folder before building")
    parser.add_option('--doc', action='store_true', dest='doc',
        help="Build only the help file")
    parser.add_option('--loc', action='store_true', dest='loc',
        help="Build only localization")
    parser.add_option('--cocoamod', action='store_true', dest='cocoamod',
        help="Build only Cocoa modules")
    parser.add_option('--updatepot', action='store_true', dest='updatepot',
        help="Generate .pot files from source code.")
    parser.add_option('--mergepot', action='store_true', dest='mergepot',
        help="Update all .po files based on .pot files.")
    (options, args) = parser.parse_args()
    return options

def build_cocoa(edition, dev):
    build_cocoa_proxy_module()
    build_cocoa_bridging_interfaces(edition)
    print("Building the cocoa layer")
    from pluginbuilder import copy_embeddable_python_dylib, get_python_header_folder, collect_dependencies
    copy_embeddable_python_dylib('build')
    if not op.exists('build/PythonHeaders'):
        os.symlink(get_python_header_folder(), 'build/PythonHeaders')
    if not op.exists('build/py'):
        os.mkdir('build/py')
    cocoa_project_path = 'cocoa/{0}'.format(edition)
    shutil.copy(op.join(cocoa_project_path, 'dg_cocoa.py'), 'build')
    specific_packages = {
        'se': ['core_se'],
        'me': ['core_me'],
        'pe': ['core_pe'],
    }[edition]
    tocopy = ['core', 'hscommon', 'cocoa/inter', 'cocoalib/cocoa'] + specific_packages
    copy_packages(tocopy, 'build')
    sys.path.insert(0, 'build')
    collect_dependencies('build/dg_cocoa.py', 'build/py', excludes=['PyQt4'])
    del sys.path[0]
    if dev:
        copy_packages(tocopy, 'build/py', create_links=True)
    # Views are not referenced by python code, so they're not found by the collector.
    copy_all('build/inter/*.so', 'build/py/inter')
    copy_sysconfig_files_for_embed('build/py')
    os.chdir(cocoa_project_path)
    print('Generating Info.plist')
    app_version = get_module_version('core_{}'.format(edition))
    filereplace('InfoTemplate.plist', 'Info.plist', version=app_version)
    print("Building the XCode project")
    args = ['-project dupeguru.xcodeproj']
    if dev:
        args.append('-configuration dev')
    else:
        args.append('-configuration release')
    args = ' '.join(args)
    os.system('xcodebuild {0}'.format(args))
    os.chdir('../..')
    print("Creating the run.py file")
    app_path = {
        'se': 'cocoa/se/dupeGuru.app',
        'me': 'cocoa/me/dupeGuru\\ ME.app',
        'pe': 'cocoa/pe/dupeGuru\\ PE.app',
    }[edition]
    tmpl = open('run_template_cocoa.py', 'rt').read()
    run_contents = tmpl.replace('{{app_path}}', app_path)
    open('run.py', 'wt').write(run_contents)

def build_qt(edition, dev):
    print("Building Qt stuff")
    print_and_do("pyrcc4 -py3 {0} > {1}".format(op.join('qt', 'base', 'dg.qrc'), op.join('qt', 'base', 'dg_rc.py')))
    print("Creating the run.py file")
    tmpl = open('run_template_qt.py', 'rt').read()
    run_contents = tmpl.replace('{{edition}}', edition)
    open('run.py', 'wt').write(run_contents)

def build_help(edition):
    print("Generating Help")
    current_path = op.abspath('.')
    help_basepath = op.join(current_path, 'help', 'en')
    help_destpath = op.join(current_path, 'build', 'help'.format(edition))
    changelog_path = op.join(current_path, 'help', 'changelog_{}'.format(edition))
    tixurl = "https://hardcoded.lighthouseapp.com/projects/31699-dupeguru/tickets/{0}"
    appname = {'se': 'dupeGuru', 'me': 'dupeGuru Music Edition', 'pe': 'dupeGuru Picture Edition'}[edition]
    homepage = 'http://www.hardcoded.net/dupeguru{}/'.format('_' + edition if edition != 'se' else '')
    confrepl = {'edition': edition, 'appname': appname, 'homepage': homepage, 'language': 'en'}
    changelogtmpl = op.join(current_path, 'help', 'changelog.tmpl')
    conftmpl = op.join(current_path, 'help', 'conf.tmpl')
    sphinxgen.gen(help_basepath, help_destpath, changelog_path, tixurl, confrepl, conftmpl, changelogtmpl)

def build_localizations(ui, edition):
    print("Building localizations")
    loc.compile_all_po('locale')
    loc.compile_all_po(op.join('hscommon', 'locale'))
    loc.merge_locale_dir(op.join('hscommon', 'locale'), 'locale')
    if op.exists(op.join('build', 'locale')):
        shutil.rmtree(op.join('build', 'locale'))
    shutil.copytree('locale', op.join('build', 'locale'), ignore=shutil.ignore_patterns('*.po', '*.pot'))
    if ui == 'cocoa':
        print("Creating lproj folders based on .po files")
        for lang in loc.get_langs('locale'):
            if lang == 'en':
                continue
            pofile = op.join('locale', lang, 'LC_MESSAGES', 'ui.po')
            for edition_folder in ['base', 'se', 'me', 'pe']:
                enlproj = op.join('cocoa', edition_folder, 'en.lproj')
                dest_lproj = op.join('cocoa', edition_folder, lang + '.lproj')
                loc.po2allxibstrings(pofile, enlproj, dest_lproj)
                if edition_folder == 'base':
                    loc.po2strings(pofile, op.join(enlproj, 'Localizable.strings'), op.join(dest_lproj, 'Localizable.strings'))
            pofile = op.join('cocoalib', 'locale', lang, 'LC_MESSAGES', 'cocoalib.po')
            loc.po2allxibstrings(pofile, op.join('cocoalib', 'en.lproj'), op.join('cocoalib', lang + '.lproj'))
        build_all_cocoa_locs('cocoalib')
        build_all_cocoa_locs(op.join('cocoa', 'base'))
        build_all_cocoa_locs(op.join('cocoa', edition))
    elif ui == 'qt':
        loc.compile_all_po(op.join('qtlib', 'locale'))
        loc.merge_locale_dir(op.join('qtlib', 'locale'), 'locale')

def build_updatepot():
    print("Building .pot files from source files")
    print("Building core.pot")
    all_cores = ['core', 'core_se', 'core_me', 'core_pe']
    loc.generate_pot(all_cores, op.join('locale', 'core.pot'), ['tr'])
    print("Building columns.pot")
    loc.generate_pot(all_cores, op.join('locale', 'columns.pot'), ['coltr'])
    print("Building ui.pot")
    ui_packages = ['qt', op.join('cocoa', 'inter')]
    loc.generate_pot(ui_packages, op.join('locale', 'ui.pot'), ['tr'])
    print("Building hscommon.pot")
    loc.generate_pot(['hscommon'], op.join('hscommon', 'locale', 'hscommon.pot'), ['tr'])
    print("Building qtlib.pot")
    loc.generate_pot(['qtlib'], op.join('qtlib', 'locale', 'qtlib.pot'), ['tr'])
    print("Building cocoalib.pot")
    loc.allstrings2pot(op.join('cocoalib', 'en.lproj'), op.join('cocoalib', 'locale', 'cocoalib.pot'))
    print("Enhancing ui.pot with Cocoa's strings files")
    loc.allstrings2pot(op.join('cocoa', 'base', 'en.lproj'), op.join('locale', 'ui.pot'),
        excludes={'core', 'message', 'columns'})
    loc.allstrings2pot(op.join('cocoa', 'se', 'en.lproj'), op.join('locale', 'ui.pot'))
    loc.allstrings2pot(op.join('cocoa', 'me', 'en.lproj'), op.join('locale', 'ui.pot'))
    loc.allstrings2pot(op.join('cocoa', 'pe', 'en.lproj'), op.join('locale', 'ui.pot'))

def build_mergepot():
    print("Updating .po files using .pot files")
    loc.merge_pots_into_pos('locale')
    loc.merge_pots_into_pos(op.join('hscommon', 'locale'))
    loc.merge_pots_into_pos(op.join('qtlib', 'locale'))
    loc.merge_pots_into_pos(op.join('cocoalib', 'locale'))

def build_cocoa_ext(extname, dest, source_files, extra_frameworks=(), extra_includes=()):
    extra_link_args = ["-framework", "CoreFoundation", "-framework", "Foundation"]
    for extra in extra_frameworks:
        extra_link_args += ['-framework', extra]
    ext = Extension(extname, source_files, extra_link_args=extra_link_args, include_dirs=extra_includes)
    setup(script_args=['build_ext', '--inplace'], ext_modules=[ext])
    fn = extname + '.so'
    assert op.exists(fn)
    move(fn, op.join(dest, fn))

def build_cocoa_proxy_module():
    print("Building Cocoa Proxy")
    import objp.p2o
    objp.p2o.generate_python_proxy_code('cocoalib/cocoa/CocoaProxy.h', 'build/CocoaProxy.m')
    build_cocoa_ext("CocoaProxy", 'cocoalib/cocoa',
        ['cocoalib/cocoa/CocoaProxy.m', 'build/CocoaProxy.m', 'build/ObjP.m', 'cocoalib/HSErrorReportWindow.m'],
        ['AppKit', 'CoreServices'],
        ['cocoalib'])

def build_cocoa_bridging_interfaces(edition):
    print("Building Cocoa Bridging Interfaces")
    import objp.o2p
    import objp.p2o
    add_to_pythonpath('cocoa')
    add_to_pythonpath('cocoalib')
    from cocoa.inter import (PyGUIObject, GUIObjectView, PyColumns, ColumnsView, PyOutline,
        OutlineView, PySelectableList, SelectableListView, PyTable, TableView, PyFairware)
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
    allclasses = [PyGUIObject, PyColumns, PyOutline, PySelectableList, PyTable, PyFairware,
        PyDetailsPanel, PyDirectoryOutline, PyPrioritizeDialog, PyPrioritizeList, PyProblemDialog,
        PyIgnoreListDialog, PyResultTable, PyStatsLabel, PyDupeGuruBase, appmod.PyDupeGuru]
    for class_ in allclasses:
        objp.o2p.generate_objc_code(class_, 'cocoa/autogen', inherit=True)
    allclasses = [GUIObjectView, ColumnsView, OutlineView, SelectableListView, TableView,
        DetailsPanelView, DirectoryOutlineView, PrioritizeDialogView, PrioritizeListView,
        IgnoreListDialogView, ResultTableView, StatsLabelView, DupeGuruView]
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

def build_normal(edition, ui, dev):
    print("Building dupeGuru {0} with UI {1}".format(edition.upper(), ui))
    add_to_pythonpath('.')
    build_help(edition)
    build_localizations(ui, edition)
    print("Building dupeGuru")
    if edition == 'pe':
        build_pe_modules(ui)
    if ui == 'cocoa':
        build_cocoa(edition, dev)
    elif ui == 'qt':
        build_qt(edition, dev)

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
    elif options.cocoamod:
        build_cocoa_proxy_module()
        build_cocoa_bridging_interfaces(edition)
    else:
        build_normal(edition, ui, dev)

if __name__ == '__main__':
    main()
