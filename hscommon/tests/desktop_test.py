import sys

import pytest

from hscommon import desktop

qt_desktop = pytest.mark.skipif(not hasattr(desktop, "QDesktopServices"), reason="needs the Qt desktop functions")


@pytest.fixture
def windows(monkeypatch):
    calls = {"shell": [], "explorer": []}
    monkeypatch.setattr(desktop, "ISWINDOWS", True, raising=False)
    monkeypatch.setattr(desktop.subprocess, "run", lambda args, **kwargs: calls["explorer"].append(args))
    return calls


@qt_desktop
def test_reveal_uses_the_shell_on_windows(windows, monkeypatch):
    monkeypatch.setattr(desktop, "_select_in_explorer", lambda path: windows["shell"].append(path) or True)
    desktop.reveal_path("some/file.jpg")
    assert len(windows["shell"]) == 1
    assert windows["explorer"] == []


@qt_desktop
def test_reveal_falls_back_to_explorer(windows, monkeypatch):
    monkeypatch.setattr(desktop, "_select_in_explorer", lambda path: False)
    desktop.reveal_path("some/file.jpg")
    [args] = windows["explorer"]
    assert args[:2] == ["explorer", "/select,"]


@pytest.mark.skipif(sys.platform != "win32", reason="Windows shell")
def test_select_in_explorer_refuses_a_missing_file(tmp_path):
    # A path the shell can't parse returns False before any window opens
    assert not desktop._select_in_explorer(str(tmp_path / "missing" / "file.jpg"))
