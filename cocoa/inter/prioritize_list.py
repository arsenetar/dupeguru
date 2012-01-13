from cocoa.inter2 import PySelectableList2, SelectableListView

class PrioritizeListView(SelectableListView):
    pass

class PyPrioritizeList(PySelectableList2):
    def moveIndexes_toIndex_(self, indexes: list, dest_index: int):
        self.model.move_indexes(indexes, dest_index)
