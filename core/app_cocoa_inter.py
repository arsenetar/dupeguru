# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-02-02
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

# Common interface for all editions' dg_cocoa unit.

from hscommon.cocoa.inter import signature, PyTable, PyOutline, PyGUIObject, PyFairware

from .gui.details_panel import DetailsPanel
from .gui.directory_tree import DirectoryTree
from .gui.problem_dialog import ProblemDialog
from .gui.problem_table import ProblemTable
from .gui.result_table import ResultTable
from .gui.stats_label import StatsLabel

class PyDupeGuruBase(PyFairware):
    #---Directories
    def addDirectory_(self, directory):
        return self.py.add_directory(directory)
    
    def removeDirectory_(self, index):
        self.py.remove_directory(index)
    
    #---Results
    def clearIgnoreList(self):
        self.py.scanner.ignore_list.Clear()
    
    def doScan(self):
        return self.py.start_scanning()
    
    def exportToXHTMLwithColumns_(self, column_ids):
        return self.py.export_to_xhtml(column_ids)
    
    def loadSession(self):
        self.py.load()
    
    def loadResultsFrom_(self, filename):
        self.py.load_from(filename)
    
    def markAll(self):
        self.py.mark_all()
    
    def markNone(self):
        self.py.mark_none()
    
    def markInvert(self):
        self.py.mark_invert()
    
    def purgeIgnoreList(self):
        self.py.purge_ignore_list()
    
    def toggleSelectedMark(self):
        self.py.toggle_selected_mark_state()
    
    def saveSession(self):
        self.py.save()
    
    def saveResultsAs_(self, filename):
        self.py.save_as(filename)
    
    #---Actions
    def addSelectedToIgnoreList(self):
        self.py.add_selected_to_ignore_list()
    
    def deleteMarked(self):
        self.py.delete_marked()
    
    def hardlinkMarked(self):
        self.py.delete_marked(replace_with_hardlinks=True)
    
    def applyFilter_(self, filter):
        self.py.apply_filter(filter)
    
    def makeSelectedReference(self):
        self.py.make_selected_reference()
    
    def copyOrMove_markedTo_recreatePath_(self, copy, destination, recreate_path):
        self.py.copy_or_move_marked(copy, destination, recreate_path)
    
    def openSelected(self):
        self.py.open_selected()
    
    def removeMarked(self):
        self.py.remove_marked()
    
    def renameSelected_(self,newname):
        return self.py.rename_selected(newname)
    
    def revealSelected(self):
        self.py.reveal_selected()
    
    def invokeCommand_(self, cmd):
        self.py.invoke_command(cmd)
    
    #---Information
    def getIgnoreListCount(self):
        return len(self.py.scanner.ignore_list)
    
    def getMarkCount(self):
        return self.py.results.mark_count
    
    @signature('i@:')
    def scanWasProblematic(self):
        return bool(self.py.results.problems)
    
    @signature('i@:')
    def resultsAreModified(self):
        return self.py.results.is_modified
    
    def deltaColumns(self):
        return list(self.py.data.DELTA_COLUMNS)
    
    #---Properties
    @signature('v@:c')
    def setMixFileKind_(self, mix_file_kind):
        self.py.scanner.mix_file_kind = mix_file_kind
    
    @signature('v@:c')
    def setEscapeFilterRegexp_(self, escape_filter_regexp):
        self.py.options['escape_filter_regexp'] = escape_filter_regexp
    
    @signature('v@:c')
    def setRemoveEmptyFolders_(self, remove_empty_folders):
        self.py.options['clean_empty_dirs'] = remove_empty_folders
    
    @signature('v@:c')
    def setIgnoreHardlinkMatches_(self, ignore_hardlink_matches):
        self.py.options['ignore_hardlink_matches'] = ignore_hardlink_matches
    
    #---Worker
    def getJobProgress(self):
        try:
            return self.py.progress.last_progress
        except AttributeError:
            # I have *no idea* why this can possible happen (last_progress is always set by
            # create_job() *before* any threaded job notification, which shows the progress panel,
            # is sent), but it happens anyway, so there we go. ref: #106
            return -1
    
    def getJobDesc(self):
        try:
            return self.py.progress.last_desc
        except AttributeError:
            # see getJobProgress
            return ''
    
    def cancelJob(self):
        self.py.progress.job_cancelled = True
    
    def jobCompleted_(self, jobid):
        self.py._job_completed(jobid)
    

class PyDetailsPanel(PyGUIObject):
    py_class = DetailsPanel
    @signature('i@:')
    def numberOfRows(self):
        return self.py.row_count()
    
    @signature('@@:@i')
    def valueForColumn_row_(self, column, row):
        return self.py.row(row)[int(column)]
    

class PyDirectoryOutline(PyOutline):
    py_class = DirectoryTree
    
    def addDirectory_(self, path):
        self.py.add_directory(path)
    

class PyResultTable(PyTable):
    py_class = ResultTable
    
    @signature('c@:')
    def powerMarkerMode(self):
        return self.py.power_marker
    
    @signature('v@:c')
    def setPowerMarkerMode_(self, value):
        self.py.power_marker = value
    
    @signature('c@:')
    def deltaValuesMode(self):
        return self.py.delta_values
    
    @signature('v@:c')
    def setDeltaValuesMode_(self, value):
        self.py.delta_values = value
    
    @signature('@@:ii')
    def valueForRow_column_(self, row_index, column):
        return self.py.get_row_value(row_index, column)
    
    @signature('c@:@')
    def renameSelected_(self, newname):
        return self.py.rename_selected(newname)
    
    @signature('v@:ic')
    def sortBy_ascending_(self, key, asc):
        self.py.sort(key, asc)
    
    def markSelected(self):
        self.py.app.toggle_selected_mark_state()
    
    def removeSelected(self):
        self.py.app.remove_selected()
    
    @signature('i@:')
    def selectedDupeCount(self):
        return self.py.selected_dupe_count
    
    # python --> cocoa
    def invalidate_markings(self):
        self.cocoa.invalidateMarkings()
    

class PyStatsLabel(PyGUIObject):
    py_class = StatsLabel
    
    def display(self):
        return self.py.display
    

class PyProblemDialog(PyGUIObject):
    py_class = ProblemDialog
    
    def revealSelected(self):
        self.py.reveal_selected_dupe()
    

class PyProblemTable(PyTable):
    py_class = ProblemTable
