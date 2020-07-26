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
from hscommon.path import Path
from hscommon.testutil import eq_

from ..fs import File
from ..directories import (
    Directories,
    DirectoryState,
    AlreadyThereError,
    InvalidPathError,
)


def create_fake_fs(rootpath):
    # We have it as a separate function because other units are using it.
    rootpath = rootpath["fs"]
    rootpath.mkdir()
    rootpath["dir1"].mkdir()
    rootpath["dir2"].mkdir()
    rootpath["dir3"].mkdir()
    fp = rootpath["file1.test"].open("w")
    fp.write("1")
    fp.close()
    fp = rootpath["file2.test"].open("w")
    fp.write("12")
    fp.close()
    fp = rootpath["file3.test"].open("w")
    fp.write("123")
    fp.close()
    fp = rootpath["dir1"]["file1.test"].open("w")
    fp.write("1")
    fp.close()
    fp = rootpath["dir2"]["file2.test"].open("w")
    fp.write("12")
    fp.close()
    fp = rootpath["dir3"]["file3.test"].open("w")
    fp.write("123")
    fp.close()
    return rootpath


testpath = None


def setup_module(module):
    # In this unit, we have tests depending on two directory structure. One with only one file in it
    # and another with a more complex structure.
    testpath = Path(tempfile.mkdtemp())
    module.testpath = testpath
    rootpath = testpath["onefile"]
    rootpath.mkdir()
    fp = rootpath["test.txt"].open("w")
    fp.write("test_data")
    fp.close()
    create_fake_fs(testpath)


def teardown_module(module):
    shutil.rmtree(str(module.testpath))


def test_empty():
    d = Directories()
    eq_(len(d), 0)
    assert "foobar" not in d


def test_add_path():
    d = Directories()
    p = testpath["onefile"]
    d.add_path(p)
    eq_(1, len(d))
    assert p in d
    assert (p["foobar"]) in d
    assert p.parent() not in d
    p = testpath["fs"]
    d.add_path(p)
    eq_(2, len(d))
    assert p in d


def test_AddPath_when_path_is_already_there():
    d = Directories()
    p = testpath["onefile"]
    d.add_path(p)
    with raises(AlreadyThereError):
        d.add_path(p)
    with raises(AlreadyThereError):
        d.add_path(p["foobar"])
    eq_(1, len(d))


def test_add_path_containing_paths_already_there():
    d = Directories()
    d.add_path(testpath["onefile"])
    eq_(1, len(d))
    d.add_path(testpath)
    eq_(len(d), 1)
    eq_(d[0], testpath)


def test_AddPath_non_latin(tmpdir):
    p = Path(str(tmpdir))
    to_add = p["unicode\u201a"]
    os.mkdir(str(to_add))
    d = Directories()
    try:
        d.add_path(to_add)
    except UnicodeDecodeError:
        assert False


def test_del():
    d = Directories()
    d.add_path(testpath["onefile"])
    try:
        del d[1]
        assert False
    except IndexError:
        pass
    d.add_path(testpath["fs"])
    del d[1]
    eq_(1, len(d))


def test_states():
    d = Directories()
    p = testpath["onefile"]
    d.add_path(p)
    eq_(DirectoryState.Normal, d.get_state(p))
    d.set_state(p, DirectoryState.Reference)
    eq_(DirectoryState.Reference, d.get_state(p))
    eq_(DirectoryState.Reference, d.get_state(p["dir1"]))
    eq_(1, len(d.states))
    eq_(p, list(d.states.keys())[0])
    eq_(DirectoryState.Reference, d.states[p])


def test_get_state_with_path_not_there():
    # When the path's not there, just return DirectoryState.Normal
    d = Directories()
    d.add_path(testpath["onefile"])
    eq_(d.get_state(testpath), DirectoryState.Normal)


def test_states_overwritten_when_larger_directory_eat_smaller_ones():
    # ref #248
    # When setting the state of a folder, we overwrite previously set states for subfolders.
    d = Directories()
    p = testpath["onefile"]
    d.add_path(p)
    d.set_state(p, DirectoryState.Excluded)
    d.add_path(testpath)
    d.set_state(testpath, DirectoryState.Reference)
    eq_(d.get_state(p), DirectoryState.Reference)
    eq_(d.get_state(p["dir1"]), DirectoryState.Reference)
    eq_(d.get_state(testpath), DirectoryState.Reference)


def test_get_files():
    d = Directories()
    p = testpath["fs"]
    d.add_path(p)
    d.set_state(p["dir1"], DirectoryState.Reference)
    d.set_state(p["dir2"], DirectoryState.Excluded)
    files = list(d.get_files())
    eq_(5, len(files))
    for f in files:
        if f.path.parent() == p["dir1"]:
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
    p = testpath["fs"]
    d.add_path(p)
    files = list(d.get_files(fileclasses=[FakeFile]))
    # We have the 3 root files and the 3 root dirs
    eq_(6, len(files))


def test_get_folders():
    d = Directories()
    p = testpath["fs"]
    d.add_path(p)
    d.set_state(p["dir1"], DirectoryState.Reference)
    d.set_state(p["dir2"], DirectoryState.Excluded)
    folders = list(d.get_folders())
    eq_(len(folders), 3)
    ref = [f for f in folders if f.is_ref]
    not_ref = [f for f in folders if not f.is_ref]
    eq_(len(ref), 1)
    eq_(ref[0].path, p["dir1"])
    eq_(len(not_ref), 2)
    eq_(ref[0].size, 1)


def test_get_files_with_inherited_exclusion():
    d = Directories()
    p = testpath["onefile"]
    d.add_path(p)
    d.set_state(p, DirectoryState.Excluded)
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
    d1.set_state(p1, DirectoryState.Reference)
    d1.set_state(p1["dir1"], DirectoryState.Excluded)
    tmpxml = str(tmpdir.join("directories_testunit.xml"))
    d1.save_to_file(tmpxml)
    d2.load_from_file(tmpxml)
    eq_(2, len(d2))
    eq_(DirectoryState.Reference, d2.get_state(p1))
    eq_(DirectoryState.Excluded, d2.get_state(p1["dir1"]))


def test_invalid_path():
    d = Directories()
    p = Path("does_not_exist")
    with raises(InvalidPathError):
        d.add_path(p)
    eq_(0, len(d))


def test_set_state_on_invalid_path():
    d = Directories()
    try:
        d.set_state(Path("foobar",), DirectoryState.Normal)
    except LookupError:
        assert False


def test_load_from_file_with_invalid_path(tmpdir):
    # This test simulates a load from file resulting in a
    # InvalidPath raise. Other directories must be loaded.
    d1 = Directories()
    d1.add_path(testpath["onefile"])
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
    p1 = Path(str(tmpdir))["hello\xe9"]
    p1.mkdir()
    p1["foo\xe9"].mkdir()
    d.add_path(p1)
    d.set_state(p1["foo\xe9"], DirectoryState.Excluded)
    tmpxml = str(tmpdir.join("directories_testunit.xml"))
    try:
        d.save_to_file(tmpxml)
    except UnicodeDecodeError:
        assert False


def test_get_files_refreshes_its_directories():
    d = Directories()
    p = testpath["fs"]
    d.add_path(p)
    files = d.get_files()
    eq_(6, len(list(files)))
    time.sleep(1)
    os.remove(str(p["dir1"]["file1.test"]))
    files = d.get_files()
    eq_(5, len(list(files)))


def test_get_files_does_not_choke_on_non_existing_directories(tmpdir):
    d = Directories()
    p = Path(str(tmpdir))
    d.add_path(p)
    p.rmtree()
    eq_([], list(d.get_files()))


def test_get_state_returns_excluded_by_default_for_hidden_directories(tmpdir):
    d = Directories()
    p = Path(str(tmpdir))
    hidden_dir_path = p[".foo"]
    p[".foo"].mkdir()
    d.add_path(p)
    eq_(d.get_state(hidden_dir_path), DirectoryState.Excluded)
    # But it can be overriden
    d.set_state(hidden_dir_path, DirectoryState.Normal)
    eq_(d.get_state(hidden_dir_path), DirectoryState.Normal)


def test_default_path_state_override(tmpdir):
    # It's possible for a subclass to override the default state of a path
    class MyDirectories(Directories):
        def _default_state_for_path(self, path, denylist):
            if "foobar" in path:
                return DirectoryState.Excluded

    d = MyDirectories()
    p1 = Path(str(tmpdir))
    p1["foobar"].mkdir()
    p1["foobar/somefile"].open("w").close()
    p1["foobaz"].mkdir()
    p1["foobaz/somefile"].open("w").close()
    d.add_path(p1)
    eq_(d.get_state(p1["foobaz"]), DirectoryState.Normal)
    eq_(d.get_state(p1["foobar"]), DirectoryState.Excluded)
    eq_(len(list(d.get_files())), 1)  # only the 'foobaz' file is there
    # However, the default state can be changed
    d.set_state(p1["foobar"], DirectoryState.Normal)
    eq_(d.get_state(p1["foobar"]), DirectoryState.Normal)
    eq_(len(list(d.get_files())), 2)


def test_exclude_list_regular_expressions(tmpdir):
    d = Directories()
    d.deny_list_str.clear()
    d.deny_list_re.clear()
    d.deny_list_re_files.clear()
    # This should only exlude the directory, but not the contained files if
    # its status is set to normal after loading it in the directory tree
    d.deny_list_str.add(r".*Recycle\.Bin$")
    d.deny_list_str.add(r"denyme.*")
    # d.deny_list_str.add(r".*denymetoo")
    # d.deny_list_str.add(r"denyme")
    d.deny_list_str.add(r".*\/\..*")
    d.deny_list_str.add(r"^\..*")
    d.compile_re()
    p1 = Path(str(tmpdir))
    # Should be ignored on Windows only (by default)
    p1["Recycle.Bin"].mkdir()
    p1["Recycle.Bin/somerecycledfile"].open("w").close()

    p1["denyme_blah.txt"].open("w").close()
    p1["blah_denymetoo"].open("w").close()
    p1["blah_denyme"].open("w").close()

    p1[".hidden_file"].open("w").close()
    p1[".hidden_dir"].mkdir()
    p1[".hidden_dir/somenormalfile1"].open("w").close()
    p1[".hidden_dir/somenormalfile2_denyme"].open("w").close()

    p1["foobar"].mkdir()
    p1["foobar/somefile"].open("w").close()
    d.add_path(p1)
    eq_(d.get_state(p1["Recycle.Bin"]), DirectoryState.Excluded)
    eq_(d.get_state(p1["foobar"]), DirectoryState.Normal)
    files = list(d.get_files())
    files = [file.name for file in files]
    print(f"first files: {files}")
    assert "somerecycledfile" not in files
    assert "denyme_blah.txt" not in files
    assert ".hidden_file" not in files
    assert "somefile1" not in files
    assert "somefile2_denyme" not in files
    # Overriding the default state from the Directory Tree
    d.set_state(p1["Recycle.Bin"], DirectoryState.Normal)
    d.set_state(p1[".hidden_dir"], DirectoryState.Normal)
    files = list(d.get_files())
    files = [file.name for file in files]
    print(f"second files: {files}")
    assert "somerecycledfile" in files
    assert "somenormalfile1" in files
