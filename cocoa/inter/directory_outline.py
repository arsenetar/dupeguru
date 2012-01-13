from objp.util import dontwrap
from cocoa.inter2 import PyOutline2, GUIObjectView

class DirectoryOutlineView(GUIObjectView):
    pass

class PyDirectoryOutline(PyOutline2):
    def addDirectory_(self, path: str):
        self.model.add_directory(path)
    
    def removeSelectedDirectory(self):
        self.model.remove_selected()
    
    # python --> cocoa
    @dontwrap
    def refresh_states(self):
        # Under cocoa, both refresh() and refresh_states() do the same thing.
        self.callback.refresh()