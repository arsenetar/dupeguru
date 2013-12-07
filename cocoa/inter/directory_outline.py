from objp.util import dontwrap
from cocoa.inter import PyOutline, GUIObjectView

class DirectoryOutlineView(GUIObjectView):
    pass

class PyDirectoryOutline(PyOutline):
    def addDirectory_(self, path: str):
        self.model.add_directory(path)
    
    def removeSelectedDirectory(self):
        self.model.remove_selected()
    
    def selectAll(self):
        self.model.select_all()
    
    # python --> cocoa
    @dontwrap
    def refresh_states(self):
        # Under cocoa, both refresh() and refresh_states() do the same thing.
        self.callback.refresh()