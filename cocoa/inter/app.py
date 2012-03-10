import logging

from objp.util import pyref, dontwrap
from jobprogress import job
import cocoa
from cocoa import install_exception_hook, proxy
from cocoa.inter import PyFairware, FairwareView
from hscommon.trans import trget

from core.app import JobType

tr = trget('ui')

JOBID2TITLE = {
    JobType.Scan: tr("Scanning for duplicates"),
    JobType.Load: tr("Loading"),
    JobType.Move: tr("Moving"),
    JobType.Copy: tr("Copying"),
    JobType.Delete: tr("Sending to Trash"),
}

class DupeGuruView(FairwareView):
    def askYesNoWithPrompt_(self, prompt: str) -> bool: pass
    def showProblemDialog(self): pass

class PyDupeGuruBase(PyFairware):
    FOLLOW_PROTOCOLS = ['Worker']
    
    @dontwrap
    def _init(self, modelclass):
        logging.basicConfig(level=logging.WARNING, format='%(levelname)s %(message)s')
        install_exception_hook()
        appdata = proxy.getAppdataPath()
        self.model = modelclass(self, appdata)
        self.progress = cocoa.ThreadedJobPerformer()
    
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
    
    #---Directories
    def addDirectory_(self, directory: str) -> int:
        return self.model.add_directory(directory)
    
    #---Results
    def clearIgnoreList(self):
        self.model.clear_ignore_list()
    
    def doScan(self):
        self.model.start_scanning()
    
    def exportToXHTML(self) -> str:
        return self.model.export_to_xhtml()
    
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
    
    def hardlinkMarked(self):
        self.model.delete_marked(replace_with_hardlinks=True)
    
    def applyFilter_(self, filter: str):
        self.model.apply_filter(filter)
    
    def makeSelectedReference(self):
        self.model.make_selected_reference()
    
    def copyOrMove_markedTo_recreatePath_(self, copy: bool, destination: str, recreate_path: bool):
        self.model.copy_or_move_marked(copy, destination, recreate_path)
    
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
    
    #---Information
    def getMarkCount(self) -> int:
        return self.model.results.mark_count
    
    def resultsAreModified(self) -> bool:
        return self.model.results.is_modified
    
    #---Properties
    def setMixFileKind_(self, mix_file_kind: bool):
        self.model.scanner.mix_file_kind = mix_file_kind
    
    def setEscapeFilterRegexp_(self, escape_filter_regexp: bool):
        self.model.options['escape_filter_regexp'] = escape_filter_regexp
    
    def setRemoveEmptyFolders_(self, remove_empty_folders: bool):
        self.model.options['clean_empty_dirs'] = remove_empty_folders
    
    def setIgnoreHardlinkMatches_(self, ignore_hardlink_matches: bool):
        self.model.options['ignore_hardlink_matches'] = ignore_hardlink_matches
    
    #---Worker
    def getJobProgress(self) -> object: # NSNumber
        try:
            return self.progress.last_progress
        except AttributeError:
            # I have *no idea* why this can possible happen (last_progress is always set by
            # create_job() *before* any threaded job notification, which shows the progress panel,
            # is sent), but it happens anyway, so there we go. ref: #106
            return -1
    
    def getJobDesc(self) -> str:
        try:
            return self.progress.last_desc
        except AttributeError:
            # see getJobProgress
            return ''
    
    def cancelJob(self):
        self.progress.job_cancelled = True
    
    def jobCompleted_(self, jobid: str):
        result = self.model._job_completed(jobid, self.progress.last_error)
        if not result:
            self.progress.reraise_if_error()
    
    #--- model --> view
    @dontwrap
    def open_path(self, path):
        proxy.openPath_(str(path))
    
    @dontwrap
    def reveal_path(self, path):
        proxy.revealPath_(str(path))
    
    @dontwrap
    def start_job(self, jobid, func, args=()):
        try:
            j = self.progress.create_job()
            args = tuple([j] + list(args))
            self.progress.run_threaded(func, args=args)
        except job.JobInProgressError:
            proxy.postNotification_userInfo_('JobInProgress', None)
        else:
            ud = {'desc': JOBID2TITLE[jobid], 'jobid':jobid}
            proxy.postNotification_userInfo_('JobStarted', ud)
    
    @dontwrap
    def ask_yes_no(self, prompt):
        return self.callback.askYesNoWithPrompt_(prompt)
    
    @dontwrap
    def show_results_window(self):
        # Not needed yet because our progress dialog is shown as a sheet of the results window,
        # which causes it to be already visible when the scan/load ends.
        # XXX Make progress sheet be a child of the folder selection window.
        pass
    
    @dontwrap
    def show_problem_dialog(self):
        self.callback.showProblemDialog()
    
