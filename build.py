# Copyright 2017 Virgil Dupras
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

import os
import shutil
import subprocess
import sys
from multiprocessing import Pool
from optparse import OptionParser
from pathlib import Path

from hscommon.build import add_to_pythonpath


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
    options, args = parser.parse_args()
    return options


def build_one_help(language):
    from hscommon import sphinxgen

    print(f"Generating Help in {language}")
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


def build_localizations():
    from hscommon import loc

    loc.compile_all_po("locale")
    locale_dest = Path("build", "locale")
    if locale_dest.exists():
        shutil.rmtree(locale_dest)
    shutil.copytree("locale", locale_dest, ignore=shutil.ignore_patterns("*.po", "*.pot"))


def build_updatepot():
    from hscommon import loc

    print("Building .pot files from source files")
    print("Building core.pot")
    loc.generate_pot(["core"], Path("locale", "core.pot"), ["tr"])
    print("Building columns.pot")
    loc.generate_pot(["core"], Path("locale", "columns.pot"), ["coltr"])


def build_mergepot():
    from hscommon import loc

    print("Updating .po files using .pot files")
    loc.merge_pots_into_pos("locale")


def build_normpo():
    from hscommon import loc

    loc.normalize_all_pos("locale")


def build_rust_engine():
    print("Building Rust Engine")
    cargo_cmd = shutil.which("cargo")
    if cargo_cmd and Path("rust_engine", "Cargo.toml").exists():
        cargo_env = os.environ.copy()
        cargo_env["PYO3_PYTHON"] = sys.executable
        subprocess.check_call([cargo_cmd, "build", "--release"], cwd="rust_engine", env=cargo_env)
        target_so = "dupeguru_rust.dll" if sys.platform == "win32" else "libdupeguru_rust.so"
        dest_so = "dupeguru_rust.pyd" if sys.platform == "win32" else "dupeguru_rust.so"
        src_path = Path("rust_engine", "target", "release", target_so)
        dest_path = Path("core", dest_so)
        if src_path.exists():
            shutil.copy2(src_path, dest_path)
            print(f"Copied {src_path} -> {dest_path}")
    else:
        print("Cargo not found or rust_engine missing, skipping Rust engine build.")


def build_pe_modules():
    print("Building PE Modules")
    # Leverage setup.py to build modules
    subprocess.check_call([sys.executable, "setup.py", "build_ext", "--inplace"])
    build_rust_engine()


def build_normal(ui=None):
    print("Building de-dup with pywebview desktop shell")
    add_to_pythonpath(".")
    build_pe_modules()
    print("Building localizations")
    build_localizations()
    build_help()


def main():
    if sys.version_info < (3, 12):
        sys.exit("Python < 3.12 is unsupported.")
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
