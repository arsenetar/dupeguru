from setuptools import setup, Extension
from pathlib import Path

exts = [
    Extension(
        "_block",
        [
            str(Path("core", "pe", "modules", "block.c")),
            str(Path("core", "pe", "modules", "common.c")),
        ],
        include_dirs=[str(Path("core", "pe", "modules"))],
    ),
    Extension(
        "_cache",
        [
            str(Path("core", "pe", "modules", "cache.c")),
            str(Path("core", "pe", "modules", "common.c")),
        ],
        include_dirs=[str(Path("core", "pe", "modules"))],
    ),
    Extension("_block_qt", [str(Path("qt", "pe", "modules", "block.c"))]),
]

headers = [str(Path("core", "pe", "modules", "common.h"))]

setup(
    ext_modules=exts,
    headers=headers,
)
