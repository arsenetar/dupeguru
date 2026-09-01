from setuptools import setup, Extension
from pathlib import Path

exts = [
    Extension(
        "dupeguru.core.pe._block",
        [
            str(Path("dupeguru", "core", "pe", "modules", "block.c")),
            str(Path("dupeguru", "core", "pe", "modules", "common.c")),
        ],
        include_dirs=[str(Path("dupeguru", "core", "pe", "modules"))],
    ),
    Extension(
        "dupeguru.core.pe._cache",
        [
            str(Path("dupeguru", "core", "pe", "modules", "cache.c")),
            str(Path("dupeguru", "core", "pe", "modules", "common.c")),
        ],
        include_dirs=[str(Path("dupeguru", "core", "pe", "modules"))],
    ),
    Extension("dupeguru.qt.pe._block_qt", [str(Path("dupeguru", "qt", "pe", "modules", "block.c"))]),
]

headers = [str(Path("dupeguru", "core", "pe", "modules", "common.h"))]

setup(ext_modules=exts, headers=headers)
