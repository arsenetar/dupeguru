"""Exercise folder selection with real Qt events and the real directory store."""

from types import SimpleNamespace

import pytest
from PyQt6.QtCore import Qt, QModelIndex, QItemSelectionModel
from PyQt6.QtTest import QTest, QSignalSpy
from PyQt6.QtWidgets import QApplication, QAbstractItemView, QComboBox

from dupeguru.core.directories import Directories
from dupeguru.core.gui.directory_tree import DirectoryTree
from dupeguru.qt.directories_model import DirectoriesModel, DirectoriesDelegate, DirectoriesView


@pytest.fixture
def folders(tmp_path):
    application = QApplication.instance() or QApplication([])
    root = tmp_path / "Albums"
    for name in ["Aaron", "Alice", "Bob"]:
        (root / name / "Record").mkdir(parents=True)
    store = Directories()
    store.add_path(root)
    tree = DirectoryTree(SimpleNamespace(directories=store))
    view = DirectoriesView()
    view.setSelectionMode(QAbstractItemView.ExtendedSelection)
    view.setSelectionBehavior(QAbstractItemView.SelectRows)
    view.setEditTriggers(QAbstractItemView.SelectedClicked | QAbstractItemView.EditKeyPressed)
    model = DirectoriesModel(tree, view)
    view.setItemDelegate(DirectoriesDelegate(view))
    view.resize(640, 480)
    view.expand(model.index(0, 0, QModelIndex()))
    view.show()
    application.processEvents()
    yield application, root, store, tree, view, model
    view.close()


def child(model, row, column=0):
    return model.index(row, column, model.index(0, 0, QModelIndex()))


def click(view, index, modifiers=Qt.NoModifier):
    QTest.mouseClick(view.viewport(), Qt.LeftButton, modifiers, view.visualRect(index).center())


@pytest.mark.parametrize("value", [0, 1, 2])
def test_ctrl_shift_bulk_and_persistence(folders, tmp_path, value):
    application, root, store, tree, view, model = folders
    # Mixed initial states also cover choosing the editor's existing value.
    store.set_state(root / "Aaron", 1)
    store.set_state(root / "Alice", 2)
    tree.update_all_states()
    click(view, child(model, 0))
    click(view, child(model, 2), Qt.ControlModifier)
    assert len(view.selectionModel().selectedRows()) == 2
    click(view, child(model, 0))
    click(view, child(model, 1), Qt.ShiftModifier)
    assert len(view.selectionModel().selectedRows()) == 2
    changed = QSignalSpy(model.dataChanged)
    assert model.setData(child(model, 0, 1), value, Qt.EditRole)
    assert len(changed) == 1
    assert len(view.selectionModel().selectedRows()) == 2
    assert view.isExpanded(model.index(0, 0, QModelIndex()))
    for name in ["Aaron", "Alice"]:
        assert store.get_state(root / name) == value
        assert store.get_state(root / name / "Record") == value
    assert store.get_state(root) == 0
    assert store.get_state(root / "Bob") == 0
    saved = tmp_path / "folders.dupegurudirs"
    store.save_to_file(saved)
    restored = Directories()
    restored.load_from_file(saved)
    assert restored.states == store.states
    tree.directories_changed()
    assert model.data(child(model, 0, 1), Qt.EditRole) == value


def test_click_state_preserves_bulk_selection(folders):
    application, root, store, tree, view, model = folders
    click(view, child(model, 0))
    click(view, child(model, 1), Qt.ControlModifier)
    click(view, child(model, 0, 1))
    QTest.qWait(QApplication.doubleClickInterval() + 50)
    assert len(view.selectionModel().selectedRows()) == 2
    editor = view.findChild(QComboBox)
    assert editor is not None
    editor.setCurrentIndex(1)
    view.itemDelegate().setModelData(editor, model, child(model, 0, 1))
    assert store.get_state(root / "Aaron") == 1
    assert store.get_state(root / "Alice") == 1


def test_single_unselected_target_and_invalid_edits(folders):
    application, root, store, tree, view, model = folders
    click(view, child(model, 0))
    assert model.setData(child(model, 1, 1), 2, Qt.EditRole)
    assert store.get_state(root / "Aaron") == 0
    assert store.get_state(root / "Alice") == 2
    assert model.setData(child(model, 0, 1), 1, Qt.EditRole)
    assert store.get_state(root / "Aaron") == 1
    assert not model.setData(QModelIndex(), 1, Qt.EditRole)
    assert not model.setData(child(model, 0), 1, Qt.EditRole)
    assert not model.setData(child(model, 0, 1), -1, Qt.EditRole)
    assert not model.setData(child(model, 0, 1), 3, Qt.EditRole)


@pytest.mark.parametrize("value", [0, 1, 2])
@pytest.mark.parametrize("reverse", [False, True])
def test_selected_parent_and_child(folders, value, reverse):
    application, root, store, tree, view, model = folders
    store.set_state(root, (value + 1) % 3)
    store.set_state(root / "Aaron" / "Record", (value + 2) % 3)
    tree.update_all_states()
    nodes = [tree[0], tree[0][0]]
    if reverse:
        nodes.reverse()
    tree.set_node_states(nodes, value)
    assert store.get_state(root) == value
    assert store.get_state(root / "Aaron") == value
    assert store.get_state(root / "Aaron" / "Record") == value
    selection = view.selectionModel()
    selection.select(child(model, 0), QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows)
    assert len(selection.selectedRows()) == 1
