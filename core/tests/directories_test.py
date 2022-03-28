# Copyright 2016 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

import os
import time
import tempfile
import shutil

from pytest import raises
from pathlib import Path
from hscommon.testutil import eq_
from hscommon.plat import ISWINDOWS

from ..fs import File
from ..directories import (
    Directories,
    DirectoryState,
    AlreadyThereError,
    InvalidPathError,
)
from ..exclude import ExcludeList, ExcludeDict


def create_fake_fs(rootpath):
    # We have it as a separate function because other units are using it.
    rootpath = rootpath.joinpath("fs")
    rootpath.mkdir()
    rootpath.joinpath("dir1").mkdir()
    rootpath.joinpath("dir2").mkdir()
    rootpath.joinpath("dir3").mkdir()
    with rootpath.joinpath("file1.test").open("wt") as fp:
        fp.write("1")
    with rootpath.joinpath("file2.test").open("wt") as fp:
        fp.write("12")
    with rootpath.joinpath("file3.test").open("wt") as fp:
        fp.write("123")
    with rootpath.joinpath("dir1", "file1.test").open("wt") as fp:
        fp.write("1")
    with rootpath.joinpath("dir2", "file2.test").open("wt") as fp:
        fp.write("12")
    with rootpath.joinpath("dir3", "file3.test").open("wt") as fp:
        fp.write("123")
    return rootpath


testpath = None


def setup_module(module):
    # In this unit, we have tests depending on two directory structure. One with only one file in it
    # and another with a more complex structure.
    testpath = Path(tempfile.mkdtemp())
    module.testpath = testpath
    rootpath = testpath.joinpath("onefile")
    rootpath.mkdir()
    with rootpath.joinpath("test.txt").open("wt") as fp:
        fp.write("test_data")
    create_fake_fs(testpath)


def teardown_module(module):
    shutil.rmtree(str(module.testpath))


def test_empty():
    d = Directories()
    eq_(len(d), 0)
    assert "foobar" not in d


def test_add_path():
    d = Directories()
    p = testpath.joinpath("onefile")
    d.add_path(p)
    eq_(1, len(d))
    assert p in d
    assert (p.joinpath("foobar")) in d
    assert p.parent not in d
    p = testpath.joinpath("fs")
    d.add_path(p)
    eq_(2, len(d))
    assert p in d


def test_add_path_when_path_is_already_there():
    d = Directories()
    p = testpath.joinpath("onefile")
    d.add_path(p)
    with raises(AlreadyThereError):
        d.add_path(p)
    with raises(AlreadyThereError):
        d.add_path(p.joinpath("foobar"))
    eq_(1, len(d))


def test_add_path_containing_paths_already_there():
    d = Directories()
    d.add_path(testpath.joinpath("onefile"))
    eq_(1, len(d))
    d.add_path(testpath)
    eq_(len(d), 1)
    eq_(d[0], testpath)


def test_add_path_non_latin(tmpdir):
    p = Path(str(tmpdir))
    to_add = p.joinpath("unicode\u201a")
    os.mkdir(str(to_add))
    d = Directories()
    try:
        d.add_path(to_add)
    except UnicodeDecodeError:
        assert False


def test_del():
    d = Directories()
    d.add_path(testpath.joinpath("onefile"))
    try:
        del d[1]
        assert False
    except IndexError:
        pass
    d.add_path(testpath.joinpath("fs"))
    del d[1]
    eq_(1, len(d))


def test_states():
    d = Directories()
    p = testpath.joinpath("onefile")
    d.add_path(p)
    eq_(DirectoryState.NORMAL, d.get_state(p))
    d.set_state(p, DirectoryState.REFERENCE)
    eq_(DirectoryState.REFERENCE, d.get_state(p))
    eq_(DirectoryState.REFERENCE, d.get_state(p.joinpath("dir1")))
    eq_(1, len(d.states))
    eq_(p, list(d.states.keys())[0])
    eq_(DirectoryState.REFERENCE, d.states[p])


def test_get_state_with_path_not_there():
    # When the path's not there, just return DirectoryState.Normal
    d = Directories()
    d.add_path(testpath.joinpath("onefile"))
    eq_(d.get_state(testpath), DirectoryState.NORMAL)


def test_states_overwritten_when_larger_directory_eat_smaller_ones():
    # ref #248
    # When setting the state of a folder, we overwrite previously set states for subfolders.
    d = Directories()
    p = testpath.joinpath("onefile")
    d.add_path(p)
    d.set_state(p, DirectoryState.EXCLUDED)
    d.add_path(testpath)
    d.set_state(testpath, DirectoryState.REFERENCE)
    eq_(d.get_state(p), DirectoryState.REFERENCE)
    eq_(d.get_state(p.joinpath("dir1")), DirectoryState.REFERENCE)
    eq_(d.get_state(testpath), DirectoryState.REFERENCE)


def test_get_files():
    d = Directories()
    p = testpath.joinpath("fs")
    d.add_path(p)
    d.set_state(p.joinpath("dir1"), DirectoryState.REFERENCE)
    d.set_state(p.joinpath("dir2"), DirectoryState.EXCLUDED)
    files = list(d.get_files())
    eq_(5, len(files))
    for f in files:
        if f.path.parent == p.joinpath("dir1"):
            assert f.is_ref
        else:
            assert not f.is_ref


def test_get_files_with_folders():
    # When fileclasses handle folders, return them and stop recursing!
    class FakeFile(File):
        @classmethod
        def can_handle(cls, path):
            return True

    d = Directories()
    p = testpath.joinpath("fs")
    d.add_path(p)
    files = list(d.get_files(fileclasses=[FakeFile]))
    # We have the 3 root files and the 3 root dirs
    eq_(6, len(files))


def test_get_folders():
    d = Directories()
    p = testpath.joinpath("fs")
    d.add_path(p)
    d.set_state(p.joinpath("dir1"), DirectoryState.REFERENCE)
    d.set_state(p.joinpath("dir2"), DirectoryState.EXCLUDED)
    folders = list(d.get_folders())
    eq_(len(folders), 3)
    ref = [f for f in folders if f.is_ref]
    not_ref = [f for f in folders if not f.is_ref]
    eq_(len(ref), 1)
    eq_(ref[0].path, p.joinpath("dir1"))
    eq_(len(not_ref), 2)
    eq_(ref[0].size, 1)


def test_get_files_with_inherited_exclusion():
    d = Directories()
    p = testpath.joinpath("onefile")
    d.add_path(p)
    d.set_state(p, DirectoryState.EXCLUDED)
    eq_([], list(d.get_files()))


def test_save_and_load(tmpdir):
    d1 = Directories()
    d2 = Directories()
    p1 = Path(str(tmpdir.join("p1")))
    p1.mkdir()
    p2 = Path(str(tmpdir.join("p2")))
    p2.mkdir()
    d1.add_path(p1)
    d1.add_path(p2)
    d1.set_state(p1, DirectoryState.REFERENCE)
    d1.set_state(p1.joinpath("dir1"), DirectoryState.EXCLUDED)
    tmpxml = str(tmpdir.join("directories_testunit.xml"))
    d1.save_to_file(tmpxml)
    d2.load_from_file(tmpxml)
    eq_(2, len(d2))
    eq_(DirectoryState.REFERENCE, d2.get_state(p1))
    eq_(DirectoryState.EXCLUDED, d2.get_state(p1.joinpath("dir1")))


def test_invalid_path():
    d = Directories()
    p = Path("does_not_exist")
    with raises(InvalidPathError):
        d.add_path(p)
    eq_(0, len(d))


def test_set_state_on_invalid_path():
    d = Directories()
    try:
        d.set_state(
            Path(
                "foobar",
            ),
            DirectoryState.NORMAL,
        )
    except LookupError:
        assert False


def test_load_from_file_with_invalid_path(tmpdir):
    # This test simulates a load from file resulting in a
    # InvalidPath raise. Other directories must be loaded.
    d1 = Directories()
    d1.add_path(testpath.joinpath("onefile"))
    # Will raise InvalidPath upon loading
    p = Path(str(tmpdir.join("toremove")))
    p.mkdir()
    d1.add_path(p)
    p.rmdir()
    tmpxml = str(tmpdir.join("directories_testunit.xml"))
    d1.save_to_file(tmpxml)
    d2 = Directories()
    d2.load_from_file(tmpxml)
    eq_(1, len(d2))


def test_unicode_save(tmpdir):
    d = Directories()
    p1 = Path(str(tmpdir), "hello\xe9")
    p1.mkdir()
    p1.joinpath("foo\xe9").mkdir()
    d.add_path(p1)
    d.set_state(p1.joinpath("foo\xe9"), DirectoryState.EXCLUDED)
    tmpxml = str(tmpdir.join("directories_testunit.xml"))
    try:
        d.save_to_file(tmpxml)
    except UnicodeDecodeError:
        assert False


def test_get_files_refreshes_its_directories():
    d = Directories()
    p = testpath.joinpath("fs")
    d.add_path(p)
    files = d.get_files()
    eq_(6, len(list(files)))
    time.sleep(1)
    os.remove(str(p.joinpath("dir1", "file1.test")))
    files = d.get_files()
    eq_(5, len(list(files)))


def test_get_files_does_not_choke_on_non_existing_directories(tmpdir):
    d = Directories()
    p = Path(str(tmpdir))
    d.add_path(p)
    shutil.rmtree(str(p))
    eq_([], list(d.get_files()))


def test_get_state_returns_excluded_by_default_for_hidden_directories(tmpdir):
    d = Directories()
    p = Path(str(tmpdir))
    hidden_dir_path = p.joinpath(".foo")
    p.joinpath(".foo").mkdir()
    d.add_path(p)
    eq_(d.get_state(hidden_dir_path), DirectoryState.EXCLUDED)
    # But it can be overriden
    d.set_state(hidden_dir_path, DirectoryState.NORMAL)
    eq_(d.get_state(hidden_dir_path), DirectoryState.NORMAL)


def test_default_path_state_override(tmpdir):
    # It's possible for a subclass to override the default state of a path
    class MyDirectories(Directories):
        def _default_state_for_path(self, path):
            if "foobar" in path.parts:
                return DirectoryState.EXCLUDED

    d = MyDirectories()
    p1 = Path(str(tmpdir))
    p1.joinpath("foobar").mkdir()
    p1.joinpath("foobar/somefile").touch()
    p1.joinpath("foobaz").mkdir()
    p1.joinpath("foobaz/somefile").touch()
    d.add_path(p1)
    eq_(d.get_state(p1.joinpath("foobaz")), DirectoryState.NORMAL)
    eq_(d.get_state(p1.joinpath("foobar")), DirectoryState.EXCLUDED)
    eq_(len(list(d.get_files())), 1)  # only the 'foobaz' file is there
    # However, the default state can be changed
    d.set_state(p1.joinpath("foobar"), DirectoryState.NORMAL)
    eq_(d.get_state(p1.joinpath("foobar")), DirectoryState.NORMAL)
    eq_(len(list(d.get_files())), 2)


class TestExcludeList:
    def setup_method(self, method):
        self.d = Directories(exclude_list=ExcludeList(union_regex=False))

    def get_files_and_expect_num_result(self, num_result):
        """Calls get_files(), get the filenames only, print for debugging.
        num_result is how many files are expected as a result."""
        print(
            f"EXCLUDED REGEX: paths {self.d._exclude_list.compiled_paths} \
files: {self.d._exclude_list.compiled_files} all: {self.d._exclude_list.compiled}"
        )
        files = list(self.d.get_files())
        files = [file.name for file in files]
        print(f"FINAL FILES {files}")
        eq_(len(files), num_result)
        return files

    def test_exclude_recycle_bin_by_default(self, tmpdir):
        regex = r"^.*Recycle\.Bin$"
        self.d._exclude_list.add(regex)
        self.d._exclude_list.mark(regex)
        p1 = Path(str(tmpdir))
        p1.joinpath("$Recycle.Bin").mkdir()
        p1.joinpath("$Recycle.Bin", "subdir").mkdir()
        self.d.add_path(p1)
        eq_(self.d.get_state(p1.joinpath("$Recycle.Bin")), DirectoryState.EXCLUDED)
        # By default, subdirs should be excluded too, but this can be overridden separately
        eq_(self.d.get_state(p1.joinpath("$Recycle.Bin", "subdir")), DirectoryState.EXCLUDED)
        self.d.set_state(p1.joinpath("$Recycle.Bin", "subdir"), DirectoryState.NORMAL)
        eq_(self.d.get_state(p1.joinpath("$Recycle.Bin", "subdir")), DirectoryState.NORMAL)

    def test_exclude_refined(self, tmpdir):
        regex1 = r"^\$Recycle\.Bin$"
        self.d._exclude_list.add(regex1)
        self.d._exclude_list.mark(regex1)
        p1 = Path(str(tmpdir))
        p1.joinpath("$Recycle.Bin").mkdir()
        p1.joinpath("$Recycle.Bin", "somefile.png").touch()
        p1.joinpath("$Recycle.Bin", "some_unwanted_file.jpg").touch()
        p1.joinpath("$Recycle.Bin", "subdir").mkdir()
        p1.joinpath("$Recycle.Bin", "subdir", "somesubdirfile.png").touch()
        p1.joinpath("$Recycle.Bin", "subdir", "unwanted_subdirfile.gif").touch()
        p1.joinpath("$Recycle.Bin", "subdar").mkdir()
        p1.joinpath("$Recycle.Bin", "subdar", "somesubdarfile.jpeg").touch()
        p1.joinpath("$Recycle.Bin", "subdar", "unwanted_subdarfile.png").touch()
        self.d.add_path(p1.joinpath("$Recycle.Bin"))

        # Filter should set the default state to Excluded
        eq_(self.d.get_state(p1.joinpath("$Recycle.Bin")), DirectoryState.EXCLUDED)
        # The subdir should inherit its parent state
        eq_(self.d.get_state(p1.joinpath("$Recycle.Bin", "subdir")), DirectoryState.EXCLUDED)
        eq_(self.d.get_state(p1.joinpath("$Recycle.Bin", "subdar")), DirectoryState.EXCLUDED)
        # Override a child path's state
        self.d.set_state(p1.joinpath("$Recycle.Bin", "subdir"), DirectoryState.NORMAL)
        eq_(self.d.get_state(p1.joinpath("$Recycle.Bin", "subdir")), DirectoryState.NORMAL)
        # Parent should keep its default state, and the other child too
        eq_(self.d.get_state(p1.joinpath("$Recycle.Bin")), DirectoryState.EXCLUDED)
        eq_(self.d.get_state(p1.joinpath("$Recycle.Bin", "subdar")), DirectoryState.EXCLUDED)
        # print(f"get_folders(): {[x for x in self.d.get_folders()]}")

        # only the 2 files directly under the Normal directory
        files = self.get_files_and_expect_num_result(2)
        assert "somefile.png" not in files
        assert "some_unwanted_file.jpg" not in files
        assert "somesubdarfile.jpeg" not in files
        assert "unwanted_subdarfile.png" not in files
        assert "somesubdirfile.png" in files
        assert "unwanted_subdirfile.gif" in files
        # Overriding the parent should enable all children
        self.d.set_state(p1.joinpath("$Recycle.Bin"), DirectoryState.NORMAL)
        eq_(self.d.get_state(p1.joinpath("$Recycle.Bin", "subdar")), DirectoryState.NORMAL)
        # all files there
        files = self.get_files_and_expect_num_result(6)
        assert "somefile.png" in files
        assert "some_unwanted_file.jpg" in files

        # This should still filter out files under directory, despite the Normal state
        regex2 = r".*unwanted.*"
        self.d._exclude_list.add(regex2)
        self.d._exclude_list.mark(regex2)
        files = self.get_files_and_expect_num_result(3)
        assert "somefile.png" in files
        assert "some_unwanted_file.jpg" not in files
        assert "unwanted_subdirfile.gif" not in files
        assert "unwanted_subdarfile.png" not in files

        if ISWINDOWS:
            regex3 = r".*Recycle\.Bin\\.*unwanted.*subdirfile.*"
        else:
            regex3 = r".*Recycle\.Bin\/.*unwanted.*subdirfile.*"
        self.d._exclude_list.rename(regex2, regex3)
        assert self.d._exclude_list.error(regex3) is None
        # print(f"get_folders(): {[x for x in self.d.get_folders()]}")
        # Directory shouldn't change its state here, unless explicitely done by user
        eq_(self.d.get_state(p1.joinpath("$Recycle.Bin", "subdir")), DirectoryState.NORMAL)
        files = self.get_files_and_expect_num_result(5)
        assert "unwanted_subdirfile.gif" not in files
        assert "unwanted_subdarfile.png" in files

        # using end of line character should only filter the directory, or file ending with subdir
        regex4 = r".*subdir$"
        self.d._exclude_list.rename(regex3, regex4)
        assert self.d._exclude_list.error(regex4) is None
        p1.joinpath("$Recycle.Bin", "subdar", "file_ending_with_subdir").touch()
        eq_(self.d.get_state(p1.joinpath("$Recycle.Bin", "subdir")), DirectoryState.EXCLUDED)
        files = self.get_files_and_expect_num_result(4)
        assert "file_ending_with_subdir" not in files
        assert "somesubdarfile.jpeg" in files
        assert "somesubdirfile.png" not in files
        assert "unwanted_subdirfile.gif" not in files
        self.d.set_state(p1.joinpath("$Recycle.Bin", "subdir"), DirectoryState.NORMAL)
        eq_(self.d.get_state(p1.joinpath("$Recycle.Bin", "subdir")), DirectoryState.NORMAL)
        # print(f"get_folders(): {[x for x in self.d.get_folders()]}")
        files = self.get_files_and_expect_num_result(6)
        assert "file_ending_with_subdir" not in files
        assert "somesubdirfile.png" in files
        assert "unwanted_subdirfile.gif" in files

        regex5 = r".*subdir.*"
        self.d._exclude_list.rename(regex4, regex5)
        # Files containing substring should be filtered
        eq_(self.d.get_state(p1.joinpath("$Recycle.Bin", "subdir")), DirectoryState.NORMAL)
        # The path should not match, only the filename, the "subdir" in the directory name shouldn't matter
        p1.joinpath("$Recycle.Bin", "subdir", "file_which_shouldnt_match").touch()
        files = self.get_files_and_expect_num_result(5)
        assert "somesubdirfile.png" not in files
        assert "unwanted_subdirfile.gif" not in files
        assert "file_ending_with_subdir" not in files
        assert "file_which_shouldnt_match" in files

        # This should match the directory only
        regex6 = r".*/.*subdir.*/.*"
        if ISWINDOWS:
            regex6 = r".*\\.*subdir.*\\.*"
        assert os.sep in regex6
        self.d._exclude_list.rename(regex5, regex6)
        self.d._exclude_list.remove(regex1)
        eq_(len(self.d._exclude_list.compiled), 1)
        assert regex1 not in self.d._exclude_list
        assert regex5 not in self.d._exclude_list
        assert self.d._exclude_list.error(regex6) is None
        assert regex6 in self.d._exclude_list
        # This still should not be affected
        eq_(self.d.get_state(p1.joinpath("$Recycle.Bin", "subdir")), DirectoryState.NORMAL)
        files = self.get_files_and_expect_num_result(5)
        # These files are under the "/subdir" directory
        assert "somesubdirfile.png" not in files
        assert "unwanted_subdirfile.gif" not in files
        # This file under "subdar" directory should not be filtered out
        assert "file_ending_with_subdir" in files
        # This file is in a directory that should be filtered out
        assert "file_which_shouldnt_match" not in files

    def test_japanese_unicode(self, tmpdir):
        p1 = Path(str(tmpdir))
        p1.joinpath("$Recycle.Bin").mkdir()
        p1.joinpath("$Recycle.Bin", "somerecycledfile.png").touch()
        p1.joinpath("$Recycle.Bin", "some_unwanted_file.jpg").touch()
        p1.joinpath("$Recycle.Bin", "subdir").mkdir()
        p1.joinpath("$Recycle.Bin", "subdir", "過去白濁物語～]_カラー.jpg").touch()
        p1.joinpath("$Recycle.Bin", "思叫物語").mkdir()
        p1.joinpath("$Recycle.Bin", "思叫物語", "なししろ会う前").touch()
        p1.joinpath("$Recycle.Bin", "思叫物語", "堂～ロ").touch()
        self.d.add_path(p1.joinpath("$Recycle.Bin"))
        regex3 = r".*物語.*"
        self.d._exclude_list.add(regex3)
        self.d._exclude_list.mark(regex3)
        # print(f"get_folders(): {[x for x in self.d.get_folders()]}")
        eq_(self.d.get_state(p1.joinpath("$Recycle.Bin", "思叫物語")), DirectoryState.EXCLUDED)
        files = self.get_files_and_expect_num_result(2)
        assert "過去白濁物語～]_カラー.jpg" not in files
        assert "なししろ会う前" not in files
        assert "堂～ロ" not in files
        # using end of line character should only filter that directory, not affecting its files
        regex4 = r".*物語$"
        self.d._exclude_list.rename(regex3, regex4)
        assert self.d._exclude_list.error(regex4) is None
        self.d.set_state(p1.joinpath("$Recycle.Bin", "思叫物語"), DirectoryState.NORMAL)
        files = self.get_files_and_expect_num_result(5)
        assert "過去白濁物語～]_カラー.jpg" in files
        assert "なししろ会う前" in files
        assert "堂～ロ" in files

    def test_get_state_returns_excluded_for_hidden_directories_and_files(self, tmpdir):
        # This regex only work for files, not paths
        regex = r"^\..*$"
        self.d._exclude_list.add(regex)
        self.d._exclude_list.mark(regex)
        p1 = Path(str(tmpdir))
        p1.joinpath("foobar").mkdir()
        p1.joinpath("foobar", ".hidden_file.txt").touch()
        p1.joinpath("foobar", ".hidden_dir").mkdir()
        p1.joinpath("foobar", ".hidden_dir", "foobar.jpg").touch()
        p1.joinpath("foobar", ".hidden_dir", ".hidden_subfile.png").touch()
        self.d.add_path(p1.joinpath("foobar"))
        # It should not inherit its parent's state originally
        eq_(self.d.get_state(p1.joinpath("foobar", ".hidden_dir")), DirectoryState.EXCLUDED)
        self.d.set_state(p1.joinpath("foobar", ".hidden_dir"), DirectoryState.NORMAL)
        # The files should still be filtered
        files = self.get_files_and_expect_num_result(1)
        eq_(len(self.d._exclude_list.compiled_paths), 0)
        eq_(len(self.d._exclude_list.compiled_files), 1)
        assert ".hidden_file.txt" not in files
        assert ".hidden_subfile.png" not in files
        assert "foobar.jpg" in files


class TestExcludeDict(TestExcludeList):
    def setup_method(self, method):
        self.d = Directories(exclude_list=ExcludeDict(union_regex=False))


class TestExcludeListunion(TestExcludeList):
    def setup_method(self, method):
        self.d = Directories(exclude_list=ExcludeList(union_regex=True))


class TestExcludeDictunion(TestExcludeList):
    def setup_method(self, method):
        self.d = Directories(exclude_list=ExcludeDict(union_regex=True))
