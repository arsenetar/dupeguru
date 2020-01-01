# Copyright 2016 Virgil Dupras

# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

import argparse

from setuptools import setup, Extension


def get_parser():
    parser = argparse.ArgumentParser(description="Build an arbitrary Python extension.")
    parser.add_argument(
        "source_files", nargs="+", help="List of source files to compile"
    )
    parser.add_argument("name", nargs=1, help="Name of the resulting extension")
    return parser


def main():
    args = get_parser().parse_args()
    print("Building {}...".format(args.name[0]))
    ext = Extension(args.name[0], args.source_files)
    setup(
        script_args=["build_ext", "--inplace"], ext_modules=[ext],
    )


if __name__ == "__main__":
    main()
