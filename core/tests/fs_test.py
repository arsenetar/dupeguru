# Created By: Virgil Dupras
# Created On: 2009-10-23
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

import hashlib
from os import urandom

from hscommon.path import Path
from hscommon.testutil import eq_
from core.tests.directories_test import create_fake_fs

from .. import fs


def create_fake_fs_with_random_data(rootpath):
    rootpath = rootpath["fs"]
    rootpath.mkdir()
    rootpath["dir1"].mkdir()
    rootpath["dir2"].mkdir()
    rootpath["dir3"].mkdir()
    fp = rootpath["file1.test"].open("wb")
    data1 = urandom(200 * 1024)  # 200KiB
    data2 = urandom(1024 * 1024)  # 1MiB
    data3 = urandom(10 * 1024 * 1024)  # 10MiB
    fp.write(data1)
    fp.close()
    fp = rootpath["file2.test"].open("wb")
    fp.write(data2)
    fp.close()
    fp = rootpath["file3.test"].open("wb")
    fp.write(data3)
    fp.close()
    fp = rootpath["dir1"]["file1.test"].open("wb")
    fp.write(data1)
    fp.close()
    fp = rootpath["dir2"]["file2.test"].open("wb")
    fp.write(data2)
    fp.close()
    fp = rootpath["dir3"]["file3.test"].open("wb")
    fp.write(data3)
    fp.close()
    return rootpath


def test_size_aggregates_subfiles(tmpdir):
    p = create_fake_fs(Path(str(tmpdir)))
    b = fs.Folder(p)
    eq_(b.size, 12)


def test_md5_aggregate_subfiles_sorted(tmpdir):
    # dir.allfiles can return child in any order. Thus, bundle.md5 must aggregate
    # all files' md5 it contains, but it must make sure that it does so in the
    # same order everytime.
    p = create_fake_fs_with_random_data(Path(str(tmpdir)))
    b = fs.Folder(p)
    md51 = fs.File(p["dir1"]["file1.test"]).md5
    md52 = fs.File(p["dir2"]["file2.test"]).md5
    md53 = fs.File(p["dir3"]["file3.test"]).md5
    md54 = fs.File(p["file1.test"]).md5
    md55 = fs.File(p["file2.test"]).md5
    md56 = fs.File(p["file3.test"]).md5
    # The expected md5 is the md5 of md5s for folders and the direct md5 for files
    folder_md51 = hashlib.md5(md51).digest()
    folder_md52 = hashlib.md5(md52).digest()
    folder_md53 = hashlib.md5(md53).digest()
    md5 = hashlib.md5(folder_md51 + folder_md52 + folder_md53 + md54 + md55 + md56)
    eq_(b.md5, md5.digest())


def test_partial_md5_aggregate_subfile_sorted(tmpdir):
    p = create_fake_fs_with_random_data(Path(str(tmpdir)))
    b = fs.Folder(p)
    md51 = fs.File(p["dir1"]["file1.test"]).md5partial
    md52 = fs.File(p["dir2"]["file2.test"]).md5partial
    md53 = fs.File(p["dir3"]["file3.test"]).md5partial
    md54 = fs.File(p["file1.test"]).md5partial
    md55 = fs.File(p["file2.test"]).md5partial
    md56 = fs.File(p["file3.test"]).md5partial
    # The expected md5 is the md5 of md5s for folders and the direct md5 for files
    folder_md51 = hashlib.md5(md51).digest()
    folder_md52 = hashlib.md5(md52).digest()
    folder_md53 = hashlib.md5(md53).digest()
    md5 = hashlib.md5(folder_md51 + folder_md52 + folder_md53 + md54 + md55 + md56)
    eq_(b.md5partial, md5.digest())

    md51 = fs.File(p["dir1"]["file1.test"]).md5samples
    md52 = fs.File(p["dir2"]["file2.test"]).md5samples
    md53 = fs.File(p["dir3"]["file3.test"]).md5samples
    md54 = fs.File(p["file1.test"]).md5samples
    md55 = fs.File(p["file2.test"]).md5samples
    md56 = fs.File(p["file3.test"]).md5samples
    # The expected md5 is the md5 of md5s for folders and the direct md5 for files
    folder_md51 = hashlib.md5(md51).digest()
    folder_md52 = hashlib.md5(md52).digest()
    folder_md53 = hashlib.md5(md53).digest()
    md5 = hashlib.md5(folder_md51 + folder_md52 + folder_md53 + md54 + md55 + md56)
    eq_(b.md5samples, md5.digest())


def test_has_file_attrs(tmpdir):
    # a Folder must behave like a file, so it must have mtime attributes
    b = fs.Folder(Path(str(tmpdir)))
    assert b.mtime > 0
    eq_(b.extension, "")
