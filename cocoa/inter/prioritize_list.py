from hscommon.cocoa.inter import signature, PySelectableList

class PyPrioritizeList(PySelectableList):
    @signature('v@:@i')
    def moveIndexes_toIndex_(self, indexes, dest_index):
        self.py.move_indexes(indexes, dest_index)
    