# Copyright 2017 Virgil Dupras
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from pathlib import Path
import sys
from optparse import OptionParser
import shutil
from multiprocessing import Pool

from setuptools import sandbox
from hscommon import sphinxgen
from hscommon.build import (
    add_to_pythonpath,
    print_and_do,
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
    parser.add_option("--doc", action="store_true", dest="doc", help="Build only the help file (en)")
    parser.add_option("--alldoc", action="store_true", dest="all_doc", help="Build only the help file in all languages")
    parser.add_option("--loc", action="store_true", dest="loc", help="Build only localization")
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
    (options, args) = parser.parse_args()
    return options


def build_one_help(language):
    print("Generating Help in {}".format(language))
    current_path = Path(".").absolute()
    changelog_path = current_path.joinpath("help", "changelog")
    tixurl = "https://github.com/arsenetar/dupeguru/issues/{}"
    changelogtmpl = current_path.joinpath("help", "changelog.tmpl")
    conftmpl = current_path.joinpath("help", "conf.tmpl")
    help_basepath = current_path.joinpath("help", language)
    help_destpath = current_path.joinpath("build", "help", language)
    confrepl = {"language": language}
    sphinxgen.gen(
        help_basepath,
        help_destpath,
        changelog_path,
        tixurl,
        confrepl,
        conftmpl,
        changelogtmpl,
    )


def build_help():
    languages = ["en", "de", "fr", "hy", "ru", "uk"]
    # Running with Pools as for some reason sphinx seems to cross contaminate the output otherwise
    with Pool(len(languages)) as p:
        p.map(build_one_help, languages)


def build_qt_localizations():
    loc.compile_all_po(Path("qtlib", "locale"))
    loc.merge_locale_dir(Path("qtlib", "locale"), "locale")


def build_localizations():
    loc.compile_all_po("locale")
    build_qt_localizations()
    locale_dest = Path("build", "locale")
    if locale_dest.exists():
        shutil.rmtree(locale_dest)
    shutil.copytree("locale", locale_dest, ignore=shutil.ignore_patterns("*.po", "*.pot"))


def build_updatepot():
    print("Building .pot files from source files")
    print("Building core.pot")
    loc.generate_pot(["core"], Path("locale", "core.pot"), ["tr"])
    print("Building columns.pot")
    loc.generate_pot(["core"], Path("locale", "columns.pot"), ["coltr"])
    print("Building ui.pot")
    # When we're not under OS X, we don't want to overwrite ui.pot because it contains Cocoa locs
    # We want to merge the generated pot with the old pot in the most preserving way possible.
    ui_packages = ["qt", Path("cocoa", "inter")]
    loc.generate_pot(ui_packages, Path("locale", "ui.pot"), ["tr"], merge=True)
    print("Building qtlib.pot")
    loc.generate_pot(["qtlib"], Path("qtlib", "locale", "qtlib.pot"), ["tr"])


def build_mergepot():
    print("Updating .po files using .pot files")
    loc.merge_pots_into_pos("locale")
    loc.merge_pots_into_pos(Path("qtlib", "locale"))
    # loc.merge_pots_into_pos(Path("cocoalib", "locale"))


def build_normpo():
    loc.normalize_all_pos("locale")
    loc.normalize_all_pos(Path("qtlib", "locale"))
    # loc.normalize_all_pos(Path("cocoalib", "locale"))


def build_pe_modules():
    print("Building PE Modules")
    # Leverage setup.py to build modules
    sandbox.run_setup("setup.py", ["build_ext", "--inplace"])


def build_normal():
    print("Building dupeGuru with UI qt")
    add_to_pythonpath(".")
    print("Building dupeGuru")
    build_pe_modules()
    print("Building localizations")
    build_localizations()
    print("Building Qt stuff")
    print_and_do("pyrcc5 {0} > {1}".format(Path("qt", "dg.qrc"), Path("qt", "dg_rc.py")))
    fix_qt_resource_file(Path("qt", "dg_rc.py"))
    build_help()


def main():
    if sys.version_info < (3, 7):
        sys.exit("Python < 3.7 is unsupported.")
    options = parse_args()
    if options.clean and Path("build").exists():
        shutil.rmtree("build")
    if not Path("build").exists():
        Path("build").mkdir()
    if options.doc:
        build_one_help("en")
    elif options.all_doc:
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
    else:
        build_normal()


if __name__ == "__main__":
    main()
