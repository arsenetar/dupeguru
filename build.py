# Copyright 2017 Virgil Dupras
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

import os
import os.path as op
from optparse import OptionParser
import shutil
from pathlib import Path

from setuptools import setup, Extension

from hscommon import sphinxgen
from hscommon.build import (
    add_to_pythonpath,
    print_and_do,
    move_all,
    fix_qt_resource_file,
)
from hscommon import loc


def parse_args():
    usage = "usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option(
        "--clean",
        action="store_true",
        dest="clean",
        help="Clean build folder before building",
    )
    parser.add_option(
        "--doc", action="store_true", dest="doc", help="Build only the help file"
    )
    parser.add_option(
        "--loc", action="store_true", dest="loc", help="Build only localization"
    )
    parser.add_option(
        "--updatepot",
        action="store_true",
        dest="updatepot",
        help="Generate .pot files from source code.",
    )
    parser.add_option(
        "--mergepot",
        action="store_true",
        dest="mergepot",
        help="Update all .po files based on .pot files.",
    )
    parser.add_option(
        "--normpo",
        action="store_true",
        dest="normpo",
        help="Normalize all PO files (do this before commit).",
    )
    parser.add_option(
        "--modules",
        action="store_true",
        dest="modules",
        help="Build the python modules.",
    )
    parser.add_option(
        "--importpo",
        action="store_true",
        dest="importpo",
        help="Import all PO files downloaded from transifex.",
    )
    (options, args) = parser.parse_args()
    return options


def build_help():
    print("Generating Help")
    current_path = op.abspath(".")
    help_basepath = op.join(current_path, "help", "en")
    help_destpath = op.join(current_path, "build", "help")
    changelog_path = op.join(current_path, "help", "changelog")
    tixurl = "https://github.com/arsenetar/dupeguru/issues/{}"
    confrepl = {"language": "en"}
    changelogtmpl = op.join(current_path, "help", "changelog.tmpl")
    conftmpl = op.join(current_path, "help", "conf.tmpl")
    sphinxgen.gen(
        help_basepath,
        help_destpath,
        changelog_path,
        tixurl,
        confrepl,
        conftmpl,
        changelogtmpl,
    )


def build_qt_localizations():
    loc.compile_all_po(op.join("qtlib", "locale"))
    loc.merge_locale_dir(op.join("qtlib", "locale"), "locale")


def build_localizations():
    loc.compile_all_po("locale")
    build_qt_localizations()
    locale_dest = op.join("build", "locale")
    if op.exists(locale_dest):
        shutil.rmtree(locale_dest)
    shutil.copytree(
        "locale", locale_dest, ignore=shutil.ignore_patterns("*.po", "*.pot")
    )


def build_updatepot():
    print("Building .pot files from source files")
    print("Building core.pot")
    loc.generate_pot(["core"], op.join("locale", "core.pot"), ["tr"])
    print("Building columns.pot")
    loc.generate_pot(["core"], op.join("locale", "columns.pot"), ["coltr"])
    print("Building ui.pot")
    # When we're not under OS X, we don't want to overwrite ui.pot because it contains Cocoa locs
    # We want to merge the generated pot with the old pot in the most preserving way possible.
    ui_packages = ["qt", op.join("cocoa", "inter")]
    loc.generate_pot(ui_packages, op.join("locale", "ui.pot"), ["tr"], merge=True)
    print("Building qtlib.pot")
    loc.generate_pot(["qtlib"], op.join("qtlib", "locale", "qtlib.pot"), ["tr"])


def build_mergepot():
    print("Updating .po files using .pot files")
    loc.merge_pots_into_pos("locale")
    loc.merge_pots_into_pos(op.join("qtlib", "locale"))
    # loc.merge_pots_into_pos(op.join("cocoalib", "locale"))


def build_normpo():
    loc.normalize_all_pos("locale")
    loc.normalize_all_pos(op.join("qtlib", "locale"))
    # loc.normalize_all_pos(op.join("cocoalib", "locale"))


def build_importpo():
    basePath = Path.cwd()
    # expect a folder named transifex with all the .po files from the exports
    translationsPath = basePath.joinpath("transifex")
    # locations where the translation files go
    qtlibPath = basePath.joinpath("qtlib", "locale")
    localePath = basePath.joinpath("locale")
    for translation in translationsPath.iterdir():
        # transifex files are named resource_lang.po so split on first '_'
        parts = translation.stem.split("_", 1)
        resource = parts[0]
        language = parts[1]
        # make sure qtlib resources go to dedicated folder
        if resource == "qtlib":
            outputPath = qtlibPath
        else:
            outputPath = localePath
        outputFolder = outputPath.joinpath(language, "LC_MESSAGES")
        # create the language folder if it is new
        if not outputFolder.exists():
            outputFolder.mkdir(parents=True)
        # copy the po file over
        shutil.copy(translation, outputFolder.joinpath(resource + ".po"))
    # normalize files after complete
    build_normpo()


def build_pe_modules():
    print("Building PE Modules")
    exts = [
        Extension(
            "_block",
            [
                op.join("core", "pe", "modules", "block.c"),
                op.join("core", "pe", "modules", "common.c"),
            ],
        ),
        Extension(
            "_cache",
            [
                op.join("core", "pe", "modules", "cache.c"),
                op.join("core", "pe", "modules", "common.c"),
            ],
        ),
    ]
    exts.append(Extension("_block_qt", [op.join("qt", "pe", "modules", "block.c")]))
    setup(
        script_args=["build_ext", "--inplace"],
        ext_modules=exts,
    )
    move_all("_block_qt*", op.join("qt", "pe"))
    move_all("_block*", op.join("core", "pe"))
    move_all("_cache*", op.join("core", "pe"))


def build_normal():
    print("Building dupeGuru with UI qt")
    add_to_pythonpath(".")
    print("Building dupeGuru")
    build_pe_modules()
    print("Building localizations")
    build_localizations()
    print("Building Qt stuff")
    print_and_do(
        "pyrcc5 {0} > {1}".format(op.join("qt", "dg.qrc"), op.join("qt", "dg_rc.py"))
    )
    fix_qt_resource_file(op.join("qt", "dg_rc.py"))
    build_help()


def main():
    options = parse_args()
    if options.clean:
        if op.exists("build"):
            shutil.rmtree("build")
    if not op.exists("build"):
        os.mkdir("build")
    if options.doc:
        build_help()
    elif options.loc:
        build_localizations()
    elif options.updatepot:
        build_updatepot()
    elif options.mergepot:
        build_mergepot()
    elif options.normpo:
        build_normpo()
    elif options.modules:
        build_pe_modules()
    elif options.importpo:
        build_importpo()
    else:
        build_normal()


if __name__ == "__main__":
    main()
