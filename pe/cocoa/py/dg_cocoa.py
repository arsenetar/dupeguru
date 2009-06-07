#!/usr/bin/env python
import objc
from AppKit import *

from dupeguru import app_pe_cocoa, scanner

# Fix py2app imports which chokes on relative imports
from dupeguru import app, app_cocoa, data, directories, engine, export, ignore, results, scanner
from dupeguru.picture import block, cache, matchbase
from hsfs import auto, manual, stats, tree, utils

class PyApp(NSObject):
    pass #fake class

class PyDupeGuru(PyApp):
    def init(self):
        self = super(PyDupeGuru,self).init()
        self.app = app_pe_cocoa.DupeGuruPE()
        return self
    
    #---Directories
    def addDirectory_(self,directory):
        return self.app.add_directory(directory)
    
    def removeDirectory_(self,index):
        self.app.RemoveDirectory(index)
    
    def setDirectory_state_(self,node_path,state):
        self.app.SetDirectoryState(node_path,state)
    
    #---Results
    def clearIgnoreList(self):
        self.app.scanner.ignore_list.Clear()
    
    def clearPictureCache(self):
        self.app.scanner.match_factory.cached_blocks.clear()
    
    def doScan(self):
        return self.app.start_scanning()
    
    def exportToXHTMLwithColumns_xslt_css_(self,column_ids,xslt_path,css_path):
        return self.app.ExportToXHTML(column_ids,xslt_path,css_path)
    
    def loadIgnoreList(self):
        self.app.LoadIgnoreList()
    
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
        self.app.SaveIgnoreList()
    
    def saveResults(self):
        self.app.Save()
    
    def refreshDetailsWithSelected(self):
        self.app.RefreshDetailsWithSelected()
    
    def selectResultNodePaths_(self,node_paths):
        self.app.SelectResultNodePaths(node_paths)
    
    def selectPowerMarkerNodePaths_(self,node_paths):
        self.app.SelectPowerMarkerNodePaths(node_paths)
    
    #---Actions
    def addSelectedToIgnoreList(self):
        self.app.AddSelectedToIgnoreList()
    
    def deleteMarked(self):
        self.app.delete_marked()
    
    def applyFilter_(self, filter):
        self.app.apply_filter(filter)
    
    def makeSelectedReference(self):
        self.app.MakeSelectedReference()
    
    def copyOrMove_markedTo_recreatePath_(self,copy,destination,recreate_path):
        self.app.copy_or_move_marked(copy, destination, recreate_path)
    
    def openSelected(self):
        self.app.OpenSelected()
    
    def removeMarked(self):
        self.app.results.perform_on_marked(lambda x:True,True)
    
    def removeSelected(self):
        self.app.RemoveSelected()
    
    def renameSelected_(self,newname):
        return self.app.RenameSelected(newname)
    
    def revealSelected(self):
        self.app.RevealSelected()
    
    #---Misc
    def sortDupesBy_ascending_(self,key,asc):
        self.app.sort_dupes(key,asc)
    
    def sortGroupsBy_ascending_(self,key,asc):
        self.app.sort_groups(key,asc)
    
    #---Information
    def getIgnoreListCount(self):
        return len(self.app.scanner.ignore_list)
    
    def getMarkCount(self):
        return self.app.results.mark_count
    
    def getStatLine(self):
        return self.app.stat_line
    
    def getOperationalErrorCount(self):
        return self.app.last_op_error_count
    
    def getSelectedDupePath(self):
        return unicode(self.app.selected_dupe_path())
    
    def getSelectedDupeRefPath(self):
        return unicode(self.app.selected_dupe_ref_path())
    
    #---Data
    @objc.signature('i@:i')
    def getOutlineViewMaxLevel_(self, tag):
        return self.app.GetOutlineViewMaxLevel(tag)
    
    @objc.signature('@@:i@')
    def getOutlineView_childCountsForPath_(self, tag, node_path):
        return self.app.GetOutlineViewChildCounts(tag, node_path)
    
    def getOutlineView_valuesForIndexes_(self,tag,node_path):
        return self.app.GetOutlineViewValues(tag,node_path)
    
    def getOutlineView_markedAtIndexes_(self,tag,node_path):
        return self.app.GetOutlineViewMarked(tag,node_path)
    
    def getTableViewCount_(self,tag):
        return self.app.GetTableViewCount(tag)
    
    def getTableViewMarkedIndexes_(self,tag):
        return self.app.GetTableViewMarkedIndexes(tag)
    
    def getTableView_valuesForRow_(self,tag,row):
        return self.app.GetTableViewValues(tag,row)
    
    #---Properties
    def setMatchScaled_(self,match_scaled):
        self.app.scanner.match_factory.match_scaled = match_scaled
    
    def setMinMatchPercentage_(self,percentage):
        self.app.scanner.match_factory.threshold = int(percentage)
    
    def setMixFileKind_(self,mix_file_kind):
        self.app.scanner.mix_file_kind = mix_file_kind
    
    def setDisplayDeltaValues_(self,display_delta_values):
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
    @objc.signature('i@:')
    def isRegistered(self):
        return self.app.registered
    
    @objc.signature('i@:@@')
    def isCodeValid_withEmail_(self, code, email):
        return self.app.is_code_valid(code, email)
    
    def setRegisteredCode_andEmail_(self, code, email):
        self.app.set_registration(code, email)
    
