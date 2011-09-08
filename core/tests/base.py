# Created By: Virgil Dupras
# Created On: 2011/09/07
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hscommon.testutil import TestApp as TestAppBase, eq_, with_app
from hscommon.path import Path
from hscommon.util import get_file_ext
from jobprogress.job import nulljob, JobCancelled

from .. import engine
from ..engine import getwords
from ..app import DupeGuru as DupeGuruBase
from ..gui.details_panel import DetailsPanel
from ..gui.directory_tree import DirectoryTree
from ..gui.result_table import ResultTable
from ..gui.prioritize_dialog import PrioritizeDialog
from . import data

class DupeGuru(DupeGuruBase):
    JOB = nulljob
    
    def __init__(self):
        DupeGuruBase.__init__(self, data, '/tmp')
    
    def _start_job(self, jobid, func, *args):
        try:
            func(self.JOB, *args)
        except JobCancelled:
            return
    
    def _get_default(self, key_name):
        return None
    
    def _set_default(self, key_name, value):
        pass

class NamedObject:
    def __init__(self, name="foobar", with_words=False, size=1, folder=None):
        self.name = name
        if folder is None:
            folder = 'basepath'
        self._folder = Path(folder)
        self.size = size
        self.md5partial = name
        self.md5 = name
        if with_words:
            self.words = getwords(name)
        self.is_ref = False
    
    def __bool__(self):
        return False #Make sure that operations are made correctly when the bool value of files is false.
    
    @property
    def path(self):
        return self._folder + self.name
    
    @property
    def folder_path(self):
        return self.path[:-1]
    
    @property
    def extension(self):
        return get_file_ext(self.name)
    
# Returns a group set that looks like that:
# "foo bar" (1)
#   "bar bleh" (1024)
#   "foo bleh" (1)
# "ibabtu" (1)
#   "ibabtu" (1)
def GetTestGroups():
    objects = [NamedObject("foo bar"),NamedObject("bar bleh"),NamedObject("foo bleh"),NamedObject("ibabtu"),NamedObject("ibabtu")]
    objects[1].size = 1024
    matches = engine.getmatches(objects) #we should have 5 matches
    groups = engine.get_groups(matches) #We should have 2 groups
    for g in groups:
        g.prioritize(lambda x:objects.index(x)) #We want the dupes to be in the same order as the list is
    groups.sort(key=len, reverse=True) # We want the group with 3 members to be first.
    return (objects,matches,groups)

class TestApp(TestAppBase):
    def __init__(self):
        make_gui = self.make_gui
        self.app = DupeGuru()
        # XXX After hscommon.testutil.TestApp has had its default parent changed to seomthing
        # customizable (with adjustments in moneyguru) we can get rid of 'parent='
        make_gui('rtable', ResultTable, parent=self.app)
        make_gui('dtree', DirectoryTree, parent=self.app)
        make_gui('dpanel', DetailsPanel, parent=self.app)
        make_gui('pdialog', PrioritizeDialog, parent=self.app)
        for elem in [self.rtable, self.dtree, self.dpanel]:
            elem.connect()
    
    #--- Helpers
    def select_pri_criterion(self, name):
        # Select a main prioritize criterion by name instead of by index. Makes tests more
        # maintainable.
        index = self.pdialog.category_list.index(name)
        self.pdialog.category_list.select(index)
