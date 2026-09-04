import os.path as op
import sys

from setuptools import Extension, setup

sys.path.insert(1, op.abspath("src"))

from hscommon.build import move_all  # noqa: E402

exts = [
    Extension("_block", [op.join("modules", "block.c"), op.join("modules", "common.c")]),
    Extension("_cache", [op.join("modules", "cache.c"), op.join("modules", "common.c")]),
]
setup(
    script_args=["build_ext", "--inplace"],
    ext_modules=exts,
)
move_all("_cache*", op.join("src", "core/pe"))
move_all("_block*", op.join("src", "core/pe"))
