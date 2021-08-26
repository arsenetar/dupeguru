from setuptools import setup, Extension
from pathlib import Path

exts = [
    Extension(
        "core.pe._block",
        [
            str(Path("core", "pe", "modules", "block.c")),
            str(Path("core", "pe", "modules", "common.c")),
        ],
        include_dirs=[str(Path("core", "pe", "modules"))],
    ),
    Extension(
        "core.pe._cache",
        [
            str(Path("core", "pe", "modules", "cache.c")),
            str(Path("core", "pe", "modules", "common.c")),
        ],
        include_dirs=[str(Path("core", "pe", "modules"))],
    ),
    Extension("qt.pe._block_qt", [str(Path("qt", "pe", "modules", "block.c"))]),
]

headers = [str(Path("core", "pe", "modules", "common.h"))]

setup(ext_modules=exts, headers=headers)
