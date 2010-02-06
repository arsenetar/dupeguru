# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-02-02
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

# Common interface for all editions' dg_cocoa unit.

from hsutil.cocoa.objcmin import NSObject

from hsutil.cocoa import signature
from hsutil.reg import InvalidCodeError

from .gui.details_panel import DetailsPanel

# Fix py2app's problems on relative imports
from core import app, app_cocoa, data, directories, engine, export, ignore, results, fs, scanner
from hsutil import conflict

class PyApp(NSObject):
    pass #fake class

class PyDupeGuruBase(PyApp):
    #---Directories
    def addDirectory_(self, directory):
        return self.app.add_directory(directory)
    
    def removeDirectory_(self, index):
        self.app.RemoveDirectory(index)
    
    def setDirectory_state_(self, node_path, state):
        self.app.SetDirectoryState(node_path, state)
    
    #---Results
    def clearIgnoreList(self):
        self.app.scanner.ignore_list.Clear()
    
    def doScan(self):
        return self.app.start_scanning()
    
    def exportToXHTMLwithColumns_(self, column_ids):
        return self.app.export_to_xhtml(column_ids)
    
    def loadIgnoreList(self):
        self.app.load_ignore_list()
    
    def loadResults(self):
        self.app.load()
    
    def markAll(self):
        self.app.results.mark_all()
    
    def markNone(self):
        self.app.results.mark_none()
    
    def markInvert(self):
        self.app.results.mark_invert()
    
    def purgeIgnoreList(self):
        self.app.PurgeIgnoreList()
    
    def toggleSelectedMark(self):
        self.app.ToggleSelectedMarkState()
    
    def saveIgnoreList(self):
        self.app.save_ignore_list()
    
    def saveResults(self):
        self.app.save()
    
    def selectedResultNodePaths(self):
        return self.app.selected_result_node_paths()
    
    def selectResultNodePaths_(self,node_paths):
        self.app.SelectResultNodePaths(node_paths)
    
    def selectedPowerMarkerNodePaths(self):
        return self.app.selected_powermarker_node_paths()
    
    def selectPowerMarkerNodePaths_(self,node_paths):
        self.app.SelectPowerMarkerNodePaths(node_paths)
    
    #---Actions
    def addSelectedToIgnoreList(self):
        self.app.add_selected_to_ignore_list()
    
    def deleteMarked(self):
        self.app.delete_marked()
    
    def applyFilter_(self, filter):
        self.app.apply_filter(filter)
    
    def makeSelectedReference(self):
        self.app.make_selected_reference()
    
    def copyOrMove_markedTo_recreatePath_(self, copy, destination, recreate_path):
        self.app.copy_or_move_marked(copy, destination, recreate_path)
    
    def openSelected(self):
        self.app.open_selected()
    
    def removeMarked(self):
        self.app.results.perform_on_marked(lambda x:True, True)
    
    def removeSelected(self):
        self.app.RemoveSelected()
    
    def renameSelected_(self,newname):
        return self.app.RenameSelected(newname)
    
    def revealSelected(self):
        self.app.RevealSelected()
    
    #---Misc
    def sortDupesBy_ascending_(self, key, asc):
        self.app.sort_dupes(key, asc)
    
    def sortGroupsBy_ascending_(self, key, asc):
        self.app.sort_groups(key, asc)
    
    #---Information
    def getIgnoreListCount(self):
        return len(self.app.scanner.ignore_list)
    
    def getMarkCount(self):
        return self.app.results.mark_count
    
    def getStatLine(self):
        return self.app.stat_line
    
    def getOperationalErrorCount(self):
        return self.app.last_op_error_count
    
    #---Data
    @signature('i@:i')
    def getOutlineViewMaxLevel_(self, tag):
        return self.app.GetOutlineViewMaxLevel(tag)
    
    @signature('@@:i@')
    def getOutlineView_childCountsForPath_(self, tag, node_path):
        return self.app.GetOutlineViewChildCounts(tag, node_path)
    
    def getOutlineView_valuesForIndexes_(self, tag, node_path):
        return self.app.GetOutlineViewValues(tag, node_path)
    
    def getOutlineView_markedAtIndexes_(self, tag, node_path):
        return self.app.GetOutlineViewMarked(tag, node_path)
    
    def getTableViewCount_(self, tag):
        return self.app.GetTableViewCount(tag)
    
    def getTableViewMarkedIndexes_(self, tag):
        return self.app.GetTableViewMarkedIndexes(tag)
    
    def getTableView_valuesForRow_(self, tag, row):
        return self.app.GetTableViewValues(tag, row)
    
    #---Properties
    def setMixFileKind_(self, mix_file_kind):
        self.app.scanner.mix_file_kind = mix_file_kind
    
    def setDisplayDeltaValues_(self, display_delta_values):
        self.app.display_delta_values= display_delta_values
    
    def setEscapeFilterRegexp_(self, escape_filter_regexp):
        self.app.options['escape_filter_regexp'] = escape_filter_regexp
    
    def setRemoveEmptyFolders_(self, remove_empty_folders):
        self.app.options['clean_empty_dirs'] = remove_empty_folders
    
    #---Worker
    def getJobProgress(self):
        return self.app.progress.last_progress
    
    def getJobDesc(self):
        return self.app.progress.last_desc
    
    def cancelJob(self):
        self.app.progress.job_cancelled = True
    
    #---Registration
    def demoLimitDescription(self):
        return self.app.DEMO_LIMIT_DESC
    
    @signature('i@:')
    def isRegistered(self):
        return self.app.registered
    
    def isCodeValid_withEmail_(self, code, email):
        try:
            self.app.validate_code(code, email)
            return None
        except InvalidCodeError as e:
            return unicode(e)
    
    def setRegisteredCode_andEmail_(self, code, email):
        self.app.set_registration(code, email)
    

class PyDetailsPanel(NSObject):
    def initWithCocoa_pyParent_(self, cocoa, pyparent):
        super(PyDetailsPanel, self).init()
        self.cocoa = cocoa
        self.py = DetailsPanel(self, pyparent.app)
        return self
    
    @signature('i@:')
    def numberOfRows(self):
        return self.py.row_count()
    
    @signature('@@:@i')
    def valueForColumn_row_(self, column, row):
        return self.py.row(row)[int(column)]
    
    # python --> cocoa
    def refresh(self):
        self.cocoa.refresh()
    
