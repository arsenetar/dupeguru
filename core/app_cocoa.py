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
    
    #--- Override
    @staticmethod
    def _open_path(path):
        NSWorkspace.sharedWorkspace().openFile_(unicode(path))
    
    @staticmethod
    def _recycle_dupe(dupe):
        # local import because first appkit import takes a lot of memory. we want to avoid it.
        directory = unicode(dupe.path[:-1])
        filename = dupe.name
        result, tag = NSWorkspace.sharedWorkspace().performFileOperation_source_destination_files_tag_(
            NSWorkspaceRecycleOperation, directory, '', [filename], None)
    
    @staticmethod
    def _reveal_path(path):
        NSWorkspace.sharedWorkspace().selectFile_inFileViewerRootedAtPath_(unicode(path), '')
    
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
    
    #---Public
    copy_or_move_marked = demo_method(app.DupeGuru.copy_or_move_marked)
    delete_marked = demo_method(app.DupeGuru.delete_marked)
    
    def PurgeIgnoreList(self):
        self.scanner.ignore_list.Filter(lambda f,s:op.exists(f) and op.exists(s))
    
    def RenameSelected(self, newname):
        try:
            d = self.selected_dupes[0]
            d.rename(newname)
            return True
        except (IndexError, fs.FSError) as e:
            logging.warning("dupeGuru Warning: %s" % unicode(e))
        return False
    
    def start_scanning(self):
        self._select_dupes([])
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
        self._select_dupes([dupe for dupe in selected if dupe is not None])
    
    def SelectPowerMarkerNodePaths(self,node_paths):
        rows = [p[0] for p in node_paths]
        dupes = [self.results.dupes[row] for row in rows if row in xrange(len(self.results.dupes))]
        self._select_dupes(dupes)
    
    def sort_dupes(self,key,asc):
        self.results.sort_dupes(key,asc,self.display_delta_values)
    
    def sort_groups(self,key,asc):
        self.results.sort_groups(key,asc)
    
