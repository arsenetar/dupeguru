# Created By: Virgil Dupras
# Created On: 2006/11/11
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import logging
import os.path as op

from jobprogress import job
from hscommon import cocoa
from hscommon.cocoa import install_exception_hook, pythonify
from hscommon.cocoa.objcmin import (NSNotificationCenter, NSUserDefaults,
    NSSearchPathForDirectoriesInDomains, NSApplicationSupportDirectory, NSUserDomainMask,
    NSWorkspace)
from hscommon.trans import tr

from . import app

JOBID2TITLE = {
    app.JOB_SCAN: tr("Scanning for duplicates"),
    app.JOB_LOAD: tr("Loading"),
    app.JOB_MOVE: tr("Moving"),
    app.JOB_COPY: tr("Copying"),
    app.JOB_DELETE: tr("Sending to Trash"),
}

class DupeGuruView:
    def __init__(self, app):
        self.app = app
    
    @staticmethod
    def open_path(path):
        NSWorkspace.sharedWorkspace().openFile_(str(path))
    
    @staticmethod
    def reveal_path(path):
        NSWorkspace.sharedWorkspace().selectFile_inFileViewerRootedAtPath_(str(path), '')
    
    def start_job(self, jobid, func, *args):
        try:
            j = self.app.progress.create_job()
            args = tuple([j] + list(args))
            self.app.progress.run_threaded(func, args=args)
        except job.JobInProgressError:
            NSNotificationCenter.defaultCenter().postNotificationName_object_('JobInProgress', self)
        else:
            ud = {'desc': JOBID2TITLE[jobid], 'jobid':jobid}
            NSNotificationCenter.defaultCenter().postNotificationName_object_userInfo_('JobStarted', self, ud)
    
    def get_default(self, key_name):
        raw = NSUserDefaults.standardUserDefaults().objectForKey_(key_name)
        result = pythonify(raw)
        return result
    
    def set_default(self, key_name, value):
        NSUserDefaults.standardUserDefaults().setObject_forKey_(value, key_name)
    
    def show_extra_fairware_reminder(self):
        NSNotificationCenter.defaultCenter().postNotificationName_object_userInfo_('ShowExtraFairwareReminder', self, None)
    

class DupeGuru(app.DupeGuru):
    def __init__(self, data_module, appdata_subdir):
        logging.basicConfig(level=logging.WARNING, format='%(levelname)s %(message)s')
        install_exception_hook()
        view = DupeGuruView(self)
        appsupport = NSSearchPathForDirectoriesInDomains(NSApplicationSupportDirectory, NSUserDomainMask, True)[0]
        appdata = op.join(appsupport, appdata_subdir)
        app.DupeGuru.__init__(self, view, data_module, appdata)
        self.progress = cocoa.ThreadedJobPerformer()
    
    #--- Public
    def start_scanning(self):
        self._select_dupes([])
        try:
            app.DupeGuru.start_scanning(self)
            return 0
        except app.NoScannableFileError:
            return 3
    
