import logging

from objp.util import pyref, dontwrap
from cocoa import install_exception_hook, install_cocoa_logger, patch_threaded_job_performer
from cocoa.inter import PyBaseApp, BaseAppView

class DupeGuruView(BaseAppView):
    def askYesNoWithPrompt_(self, prompt: str) -> bool: pass
    def showResultsWindow(self): pass
    def showProblemDialog(self): pass
    def selectDestFolderWithPrompt_(self, prompt: str) -> str: pass
    def selectDestFileWithPrompt_extension_(self, prompt: str, extension: str) -> str: pass

class PyDupeGuruBase(PyBaseApp):
    @dontwrap
    def _init(self, modelclass):
        logging.basicConfig(level=logging.WARNING, format='%(levelname)s %(message)s')
        install_exception_hook('https://github.com/hsoft/dupeguru/issues')
        install_cocoa_logger()
        patch_threaded_job_performer()
        self.model = modelclass(self)
    
    #---Sub-proxies
    def detailsPanel(self) -> pyref:
        return self.model.details_panel
    
    def directoryTree(self) -> pyref:
        return self.model.directory_tree
    
    def problemDialog(self) -> pyref:
        return self.model.problem_dialog
    
    def statsLabel(self) -> pyref:
        return self.model.stats_label
    
    def resultTable(self) -> pyref:
        return self.model.result_table
    
    def ignoreListDialog(self) -> pyref:
        return self.model.ignore_list_dialog
    
    def progressWindow(self) -> pyref:
        return self.model.progress_window
    
    def deletionOptions(self) -> pyref:
        return self.model.deletion_options
    
    #---Directories
    def addDirectory_(self, directory: str):
        self.model.add_directory(directory)
    
    #---Results
    def doScan(self):
        self.model.start_scanning()
    
    def exportToXHTML(self):
        self.model.export_to_xhtml()
    
    def exportToCSV(self):
        self.model.export_to_csv()
    
    def loadSession(self):
        self.model.load()
    
    def loadResultsFrom_(self, filename: str):
        self.model.load_from(filename)
    
    def markAll(self):
        self.model.mark_all()
    
    def markNone(self):
        self.model.mark_none()
    
    def markInvert(self):
        self.model.mark_invert()
    
    def purgeIgnoreList(self):
        self.model.purge_ignore_list()
    
    def toggleSelectedMark(self):
        self.model.toggle_selected_mark_state()
    
    def saveSession(self):
        self.model.save()
    
    def saveResultsAs_(self, filename: str):
        self.model.save_as(filename)
    
    #---Actions
    def addSelectedToIgnoreList(self):
        self.model.add_selected_to_ignore_list()
    
    def deleteMarked(self):
        self.model.delete_marked()
    
    def applyFilter_(self, filter: str):
        self.model.apply_filter(filter)
    
    def makeSelectedReference(self):
        self.model.make_selected_reference()
    
    def copyMarked(self):
        self.model.copy_or_move_marked(copy=True)
    
    def moveMarked(self):
        self.model.copy_or_move_marked(copy=False)
    
    def openSelected(self):
        self.model.open_selected()
    
    def removeMarked(self):
        self.model.remove_marked()
    
    def removeSelected(self):
        self.model.remove_selected()
    
    def revealSelected(self):
        self.model.reveal_selected()

    def invokeCustomCommand(self):
        self.model.invoke_custom_command()
    
    def showIgnoreList(self):
        self.model.ignore_list_dialog.show()
    
    #---Information
    def getScanOptions(self) -> list:
        return [o.label for o in self.model.SCANNER_CLASS.get_scan_options()]
    
    def resultsAreModified(self) -> bool:
        return self.model.results.is_modified
    
    #---Properties
    def setMixFileKind_(self, mix_file_kind: bool):
        self.model.options['mix_file_kind'] = mix_file_kind
    
    def setEscapeFilterRegexp_(self, escape_filter_regexp: bool):
        self.model.options['escape_filter_regexp'] = escape_filter_regexp
    
    def setRemoveEmptyFolders_(self, remove_empty_folders: bool):
        self.model.options['clean_empty_dirs'] = remove_empty_folders
    
    def setIgnoreHardlinkMatches_(self, ignore_hardlink_matches: bool):
        self.model.options['ignore_hardlink_matches'] = ignore_hardlink_matches
    
    def setCopyMoveDestType_(self, copymove_dest_type: int):
        self.model.options['copymove_dest_type'] = copymove_dest_type
    
    #--- model --> view
    @dontwrap
    def ask_yes_no(self, prompt):
        return self.callback.askYesNoWithPrompt_(prompt)
    
    @dontwrap
    def show_results_window(self):
        self.callback.showResultsWindow()
    
    @dontwrap
    def show_problem_dialog(self):
        self.callback.showProblemDialog()
    
    @dontwrap
    def select_dest_folder(self, prompt):
        return self.callback.selectDestFolderWithPrompt_(prompt)
    
    @dontwrap
    def select_dest_file(self, prompt, extension):
        return self.callback.selectDestFileWithPrompt_extension_(prompt, extension)
    
