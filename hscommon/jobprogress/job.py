# Created By: Virgil Dupras
# Created On: 2004/12/20
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

class JobCancelled(Exception):
    "The user has cancelled the job"

class JobInProgressError(Exception): 
    "A job is already being performed, you can't perform more than one at the same time."

class JobCountError(Exception):
    "The number of jobs started have exceeded the number of jobs allowed"

class Job:
    """Manages a job's progression and return it's progression through a callback.
    
    Note that this class is not foolproof. For example, you could call
    start_subjob, and then call add_progress from the parent job, and nothing
    would stop you from doing it. However, it would mess your progression
    because it is the sub job that is supposed to drive the progression.
    Another example would be to start a subjob, then start another, and call
    add_progress from the old subjob. Once again, it would mess your progression.
    There are no stops because it would remove the lightweight aspect of the
    class (A Job would need to have a Parent instead of just a callback,
    and the parent could be None. A lot of checks for nothing.).
    Another one is that nothing stops you from calling add_progress right after
    SkipJob.
    """
    #---Magic functions
    def __init__(self, job_proportions, callback):
        """Initialize the Job with 'jobcount' jobs. Start every job with
        start_job(). Every time the job progress is updated, 'callback' is called
        'callback' takes a 'progress' int param, and a optional 'desc'
        parameter. Callback must return false if the job must be cancelled.
        """
        if not hasattr(callback, '__call__'):
            raise TypeError("'callback' MUST be set when creating a Job")
        if isinstance(job_proportions, int):
            job_proportions = [1] * job_proportions
        self._job_proportions = list(job_proportions)
        self._jobcount = sum(job_proportions)
        self._callback = callback
        self._current_job = 0
        self._passed_jobs = 0
        self._progress = 0
        self._currmax = 1
    
    #---Private
    def _subjob_callback(self, progress, desc=''):
        """This is the callback passed to children jobs.
        """
        self.set_progress(progress, desc)
        return True #if JobCancelled has to be raised, it will be at the highest level
    
    def _do_update(self, desc):
        """Calls the callback function with a % progress as a parameter.
        
        The parameter is a int in the 0-100 range.
        """
        if self._current_job:
            passed_progress = self._passed_jobs * self._currmax
            current_progress = self._current_job * self._progress
            total_progress = self._jobcount * self._currmax
            progress = ((passed_progress + current_progress) * 100) // total_progress
        else:
            progress = -1 # indeterminate
        # It's possible that callback doesn't support a desc arg
        result = self._callback(progress, desc) if desc else self._callback(progress)
        if not result:
            raise JobCancelled()
    
    #---Public
    def add_progress(self, progress=1, desc=''):
        self.set_progress(self._progress + progress, desc)
    
    def check_if_cancelled(self):
        self._do_update('')
    
    def iter_with_progress(self, sequence, desc_format=None, every=1):
        ''' Iterate through sequence while automatically adding progress.
        '''
        desc = ''
        if desc_format:
            desc = desc_format % (0, len(sequence))
        self.start_job(len(sequence), desc)
        for i, element in enumerate(sequence, start=1):
            yield element
            if i % every == 0:
                if desc_format:
                    desc = desc_format % (i, len(sequence))
                self.add_progress(progress=every, desc=desc)
        if desc_format:
            desc = desc_format % (len(sequence), len(sequence))
        self.set_progress(100, desc)
    
    def start_job(self, max_progress=100, desc=''):
        """Begin work on the next job. You must not call start_job more than
        'jobcount' (in __init__) times.
        'max' is the job units you are to perform.
        'desc' is the description of the job.
        """
        self._passed_jobs += self._current_job
        try:
            self._current_job = self._job_proportions.pop(0)
        except IndexError:
            raise JobCountError()
        self._progress = 0
        self._currmax = max(1, max_progress)
        self._do_update(desc)
    
    def start_subjob(self, job_proportions, desc=''):
        """Starts a sub job. Use this when you want to split a job into
        multiple smaller jobs. Pretty handy when starting a process where you
        know how many subjobs you will have, but don't know the work unit count
        for every of them.
        returns the Job object
        """
        self.start_job(100, desc)
        return Job(job_proportions, self._subjob_callback)
    
    def set_progress(self, progress, desc=''):
        """Sets the progress of the current job to 'progress', and call the
        callback
        """
        self._progress = progress
        if self._progress > self._currmax:
            self._progress = self._currmax
        if self._progress < 0:
            self._progress = 0
        self._do_update(desc)
    

class NullJob:
    def __init__(self, *args, **kwargs):
        pass
    
    def add_progress(self, *args, **kwargs):
        pass
    
    def check_if_cancelled(self):
        pass
    
    def iter_with_progress(self, sequence, *args, **kwargs):
        return iter(sequence)
    
    def start_job(self, *args, **kwargs):
        pass
    
    def start_subjob(self, *args, **kwargs):
        return NullJob()
    
    def set_progress(self, *args, **kwargs):
        pass
    

nulljob = NullJob()
