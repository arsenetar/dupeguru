#!/usr/bin/env python
"""
Unit Name: dupeguru.app_cocoa
Created By: Virgil Dupras
Created On: 2006/11/11
Last modified by:$Author: virgil $
Last modified on:$Date: 2009-05-28 16:33:32 +0200 (Thu, 28 May 2009) $
                 $Revision: 4392 $
Copyright 2006 Hardcoded Software (http://www.hardcoded.net)
"""
from AppKit import *
import logging
import os.path as op

import hsfs as fs
from hsutil import io, cocoa, job
from hsutil.cocoa import install_exception_hook
from hsutil.misc import stripnone
from hsutil.reg import RegistrationRequired

import export, app, data

JOBID2TITLE = {
    app.JOB_SCAN: "Scanning for duplicates",
    app.JOB_LOAD: "Loading",
    app.JOB_MOVE: "Moving",
    app.JOB_COPY: "Copying",
    app.JOB_DELETE: "Sending to Trash",
}

def demo_method(method):
    def wrapper(self, *args, **kwargs):
        try:
            return method(self, *args, **kwargs)
        except RegistrationRequired:
            NSNotificationCenter.defaultCenter().postNotificationName_object_('RegistrationRequired', self)
    
    return wrapper

class DupeGuru(app.DupeGuru):
    def __init__(self, data_module, appdata_subdir, appid):
        LOGGING_LEVEL = logging.DEBUG if NSUserDefaults.standardUserDefaults().boolForKey_('debug') else logging.WARNING
        logging.basicConfig(level=LOGGING_LEVEL, format='%(levelname)s %(message)s')
        logging.debug('started in debug mode')
        install_exception_hook()
        if data_module is None:
            data_module = data
        appdata = op.expanduser(op.join('~', '.hsoftdata', appdata_subdir))
        app.DupeGuru.__init__(self, data_module, appdata, appid)
        self.progress = cocoa.ThreadedJobPerformer()
        self.display_delta_values = False
        self.selected_dupes = []
        self.RefreshDetailsTable(None,None)
    
    #--- Override
    @staticmethod
    def _recycle_dupe(dupe):
        if not io.exists(dupe.path):
            dupe.parent = None
            return True
        directory = unicode(dupe.parent.path)
        filename = dupe.name
        result, tag = NSWorkspace.sharedWorkspace().performFileOperation_source_destination_files_tag_(
            NSWorkspaceRecycleOperation, directory, '', [filename])
        if not io.exists(dupe.path):
            dupe.parent = None
            return True
        logging.warning('Could not send %s to trash. tag: %d' % (unicode(dupe.path), tag))
        return False
    
    def _start_job(self, jobid, func):
        try:
            j = self.progress.create_job()
            self.progress.run_threaded(func, args=(j, ))
        except job.JobInProgressError:
            NSNotificationCenter.defaultCenter().postNotificationName_object_('JobInProgress', self)
        else:
            ud = {'desc': JOBID2TITLE[jobid], 'jobid':jobid}
            NSNotificationCenter.defaultCenter().postNotificationName_object_userInfo_('JobStarted', self, ud)
    
    #---Helpers
    def GetObjects(self,node_path):
        #returns a tuple g,d
        try:
            g = self.results.groups[node_path[0]]
            if len(node_path) == 2:
                return (g,self.results.groups[node_path[0]].dupes[node_path[1]])
            else:
                return (g,None)
        except IndexError:
            return (None,None)
    
    def GetDirectory(self,node_path,curr_dir=None):
        if not node_path:
            return curr_dir
        if curr_dir is not None:
            l = curr_dir.dirs
        else:
            l = self.directories
        d = l[node_path[0]]
        return self.GetDirectory(node_path[1:],d)
    
    def RefreshDetailsTable(self,dupe,group):
        l1 = self.data.GetDisplayInfo(dupe,group,False)
        if group is not None:
            l2 = self.data.GetDisplayInfo(group.ref,group,False)
        else:
            l2 = l1 #To have a list of empty '---' values
        names = [c['display'] for c in self.data.COLUMNS]
        self.details_table = zip(names,l1,l2)
    
    #---Public
    def AddSelectedToIgnoreList(self):
        for dupe in self.selected_dupes:
            self.add_to_ignore_list(dupe)
    
    copy_or_move_marked = demo_method(app.DupeGuru.copy_or_move_marked)
    delete_marked = demo_method(app.DupeGuru.delete_marked)

    def ExportToXHTML(self,column_ids,xslt_path,css_path):
        columns = []
        for index,column in enumerate(self.data.COLUMNS):
            display = column['display']
            enabled = str(index) in column_ids
            columns.append((display,enabled))
        xml_path = op.join(self.appdata,'results_export.xml')
        self.results.save_to_xml(xml_path,self.data.GetDisplayInfo)
        return export.export_to_xhtml(xml_path,xslt_path,css_path,columns)
    
    def MakeSelectedReference(self):
        self.make_reference(self.selected_dupes)
    
    def OpenSelected(self):
        if self.selected_dupes:
            path = unicode(self.selected_dupes[0].path)
            NSWorkspace.sharedWorkspace().openFile_(path)
    
    def PurgeIgnoreList(self):
        self.scanner.ignore_list.Filter(lambda f,s:op.exists(f) and op.exists(s))
    
    def RefreshDetailsWithSelected(self):
        if self.selected_dupes:
            self.RefreshDetailsTable(
                self.selected_dupes[0],
                self.results.get_group_of_duplicate(self.selected_dupes[0])
            )
        else:
            self.RefreshDetailsTable(None,None)
    
    def RemoveDirectory(self,index):
        try:
            del self.directories[index]
        except IndexError:
            pass
    
    def RemoveSelected(self):
        self.results.remove_duplicates(self.selected_dupes)
    
    def RenameSelected(self,newname):
        try:
            d = self.selected_dupes[0]
            d = d.move(d.parent,newname)
            return True
        except (IndexError,fs.FSError),e:
            logging.warning("dupeGuru Warning: %s" % str(e))
        return False
    
    def RevealSelected(self):
        if self.selected_dupes:
            path = unicode(self.selected_dupes[0].path)
            NSWorkspace.sharedWorkspace().selectFile_inFileViewerRootedAtPath_(path,'')
    
    def start_scanning(self):
        self.RefreshDetailsTable(None, None)
        try:
            app.DupeGuru.start_scanning(self)
            return 0
        except app.NoScannableFileError:
            return 3
        except app.AllFilesAreRefError:
            return 1
    
    def selected_result_node_paths(self):
        def get_path(dupe):
            try:
                group = self.results.get_group_of_duplicate(dupe)
                groupindex = self.results.groups.index(group)
                if dupe is group.ref:
                    return [groupindex]
                dupeindex = group.dupes.index(dupe)
                return [groupindex, dupeindex]
            except ValueError: # dupe not in there
                return None
        
        dupes = self.selected_dupes
        return stripnone(get_path(dupe) for dupe in dupes)
    
    def selected_powermarker_node_paths(self):
        def get_path(dupe):
            try:
                dupeindex = self.results.dupes.index(dupe)
                return [dupeindex]
            except ValueError: # dupe not in there
                return None
        
        dupes = self.selected_dupes
        return stripnone(get_path(dupe) for dupe in dupes)
    
    def SelectResultNodePaths(self,node_paths):
        def extract_dupe(t):
            g,d = t
            if d is not None:
                return d
            else:
                if g is not None:
                    return g.ref
        
        selected = [extract_dupe(self.GetObjects(p)) for p in node_paths]
        self.selected_dupes = [dupe for dupe in selected if dupe is not None]
    
    def SelectPowerMarkerNodePaths(self,node_paths):
        rows = [p[0] for p in node_paths]
        self.selected_dupes = [
            self.results.dupes[row] for row in rows if row in xrange(len(self.results.dupes))
        ]
    
    def SetDirectoryState(self,node_path,state):
        d = self.GetDirectory(node_path)
        self.directories.set_state(d.path,state)
    
    def sort_dupes(self,key,asc):
        self.results.sort_dupes(key,asc,self.display_delta_values)
    
    def sort_groups(self,key,asc):
        self.results.sort_groups(key,asc)
    
    def ToggleSelectedMarkState(self):
        for dupe in self.selected_dupes:
            self.results.mark_toggle(dupe)
    
    #---Data
    def GetOutlineViewMaxLevel(self, tag):
        if tag == 0:
            return 2
        elif tag == 1:
            return 0
        elif tag == 2:
            return 1
    
    def GetOutlineViewChildCounts(self, tag, node_path):
        if self.progress._job_running:
            return []
        if tag == 0: #Normal results
            assert not node_path # no other value is possible
            return [len(g.dupes) for g in self.results.groups]
        elif tag == 1: #Directories
            dirs = self.GetDirectory(node_path).dirs if node_path else self.directories
            return [d.dircount for d in dirs]
        else: #Power Marker
            assert not node_path # no other value is possible
            return [0 for d in self.results.dupes]
    
    def GetOutlineViewValues(self, tag, node_path):
        if self.progress._job_running:
            return
        if not node_path:
            return
        if tag in (0,2): #Normal results / Power Marker
            if tag == 0:
                g, d = self.GetObjects(node_path)
                if d is None:
                    d = g.ref
            else:
                d = self.results.dupes[node_path[0]]
                g = self.results.get_group_of_duplicate(d)
            result = self.data.GetDisplayInfo(d, g, self.display_delta_values)
            return result
        elif tag == 1: #Directories
            d = self.GetDirectory(node_path)
            return [
                d.name,
                self.directories.get_state(d.path)
            ]
    
    def GetOutlineViewMarked(self, tag, node_path):
        # 0=unmarked 1=marked 2=unmarkable
        if self.progress._job_running:
            return
        if not node_path:
            return 2
        if tag == 1: #Directories
            return 2
        if tag == 0: #Normal results
            g, d = self.GetObjects(node_path)
        else: #Power Marker
            d = self.results.dupes[node_path[0]]
        if (d is None) or (not self.results.is_markable(d)):
            return 2
        elif self.results.is_marked(d):
            return 1
        else:
            return 0
    
    def GetTableViewCount(self, tag):
        if self.progress._job_running:
            return 0
        return len(self.details_table)
    
    def GetTableViewMarkedIndexes(self,tag):
        return []
    
    def GetTableViewValues(self,tag,row):
        return self.details_table[row]
    

