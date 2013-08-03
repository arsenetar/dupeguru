# Created On: 2013/07/01
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from jobprogress.performer import ThreadedJobPerformer

from .base import GUIObject
from .text_field import TextField

class ProgressWindow(GUIObject, ThreadedJobPerformer):
    def __init__(self, finish_func):
        # finish_func(jobid) is the function that is called when a job is completed.
        GUIObject.__init__(self)
        ThreadedJobPerformer.__init__(self)
        self._finish_func = finish_func
        self.jobdesc_textfield = TextField()
        self.progressdesc_textfield = TextField()
        self.jobid = None
    
    def cancel(self):
        self.user_cancelled = True
    
    def pulse(self):
        # Call this regularly from the GUI main run loop.
        # the values might change before setValue happens
        last_progress = self.last_progress
        last_desc = self.last_desc
        if not self._job_running or last_progress is None:
            self.view.close()
            self.reraise_if_error()
            if not self.job_cancelled:
                self._finish_func(self.jobid)
            return
        if self.job_cancelled:
            return
        if last_desc:
            self.progressdesc_textfield.text = last_desc
        self.view.set_progress(last_progress)
    
    def run(self, jobid, title, target, args=()):
        # target is a function with its first argument being a Job. It can then be followed by other
        # arguments which are passed as `args`.
        self.jobid = jobid
        self.user_cancelled = False
        self.progressdesc_textfield.text = ''
        j = self.create_job()
        args = tuple([j] + list(args))
        self.run_threaded(target, args)
        self.jobdesc_textfield.text = title
        self.view.show()
    
