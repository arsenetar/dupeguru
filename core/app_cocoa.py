# Created By: Virgil Dupras
# Created On: 2006/11/11
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import logging
import os.path as op

from hsutil import cocoa, job
from hsutil.cocoa import install_exception_hook
from hsutil.cocoa.objcmin import (NSNotificationCenter, NSUserDefaults,
    NSSearchPathForDirectoriesInDomains, NSApplicationSupportDirectory, NSUserDomainMask,
    NSWorkspace, NSWorkspaceRecycleOperation)
from hsutil.misc import stripnone
from hsutil.reg import RegistrationRequired

from . import app, fs

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
        appsupport = NSSearchPathForDirectoriesInDomains(NSApplicationSupportDirectory, NSUserDomainMask, True)[0]
        appdata = op.join(appsupport, appdata_subdir)
        app.DupeGuru.__init__(self, data_module, appdata, appid)
        self.progress = cocoa.ThreadedJobPerformer()
        self.display_delta_values = False
        self.selected_dupes = []
        self.RefreshDetailsTable(None,None)
    
    #--- Override
    @staticmethod
    def _recycle_dupe(dupe):
        # local import because first appkit import takes a lot of memory. we want to avoid it.
        directory = unicode(dupe.path[:-1])
        filename = dupe.name
        result, tag = NSWorkspace.sharedWorkspace().performFileOperation_source_destination_files_tag_(
            NSWorkspaceRecycleOperation, directory, '', [filename], None)
    
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
    
    def get_folder_path(self, node_path, curr_path=None):
        if not node_path:
            return curr_path
        current_index = node_path[0]
        if curr_path is None:
            curr_path = self.directories[current_index]
        else:
            curr_path = self.directories.get_subfolders(curr_path)[current_index]
        return self.get_folder_path(node_path[1:], curr_path)
    
    def RefreshDetailsTable(self,dupe,group):
        l1 = self._get_display_info(dupe, group, False)
        # we don't want the two sides of the table to display the stats for the same file
        ref = group.ref if group is not None and group.ref is not dupe else None
        l2 = self._get_display_info(ref, group, False)
        names = [c['display'] for c in self.data.COLUMNS]
        self.details_table = zip(names,l1,l2)
    
    #---Public
    def AddSelectedToIgnoreList(self):
        for dupe in self.selected_dupes:
            self.add_to_ignore_list(dupe)
    
    copy_or_move_marked = demo_method(app.DupeGuru.copy_or_move_marked)
    delete_marked = demo_method(app.DupeGuru.delete_marked)

    def MakeSelectedReference(self):
        self.make_reference(self.selected_dupes)
    
    def OpenSelected(self):
        # local import because first appkit import takes a lot of memory. we want to avoid it.
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
    
    def RenameSelected(self, newname):
        try:
            d = self.selected_dupes[0]
            d.rename(newname)
            return True
        except (IndexError, fs.FSError) as e:
            logging.warning("dupeGuru Warning: %s" % unicode(e))
        return False
    
    def RevealSelected(self):
        # local import because first appkit import takes a lot of memory. we want to avoid it.
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
    
    def SetDirectoryState(self, node_path, state):
        p = self.get_folder_path(node_path)
        self.directories.set_state(p, state)
    
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
            try:
                if node_path:
                    path = self.get_folder_path(node_path)
                    subfolders = self.directories.get_subfolders(path)
                else:
                    subfolders = self.directories
                return [len(self.directories.get_subfolders(path)) for path in subfolders]
            except IndexError: # node_path out of range
                return []
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
            result = self._get_display_info(d, g, self.display_delta_values)
            return result
        elif tag == 1: #Directories
            try:
                path = self.get_folder_path(node_path)
                name = unicode(path) if len(node_path) == 1 else path[-1]
                return [name, self.directories.get_state(path)]
            except IndexError: # node_path out of range
                return []
    
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
    

