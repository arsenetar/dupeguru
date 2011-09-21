from hscommon.cocoa.inter import PyOutline

from core.gui.directory_tree import DirectoryTree

class PyDirectoryOutline(PyOutline):
    py_class = DirectoryTree
    
    def addDirectory_(self, path):
        self.py.add_directory(path)
    
    # python --> cocoa
    def refresh_states(self):
        # Under cocoa, both refresh() and refresh_states() do the same thing.
        self.cocoa.refresh()