# Created By: Virgil Dupras
# Created On: 2011/09/07
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hscommon.testutil import TestApp as TestAppBase, eq_, with_app
from hscommon.path import Path
from hscommon.util import get_file_ext, format_size
from hscommon.gui.column import Column
from jobprogress.job import nulljob, JobCancelled

from .. import engine
from .. import prioritize
from ..engine import getwords
from ..app import DupeGuru as DupeGuruBase, cmp_value
from ..gui.details_panel import DetailsPanel
from ..gui.directory_tree import DirectoryTree
from ..gui.result_table import ResultTable as ResultTableBase
from ..gui.prioritize_dialog import PrioritizeDialog

class DupeGuruView:
    JOB = nulljob
    
    def __init__(self):
        self.messages = []
    
    def start_job(self, jobid, func, args=()):
        try:
            func(self.JOB, *args)
        except JobCancelled:
            return
    
    def get_default(self, key_name):
        return None
    
    def set_default(self, key_name, value):
        pass
    
    def show_message(self, msg):
        self.messages.append(msg)
    
    def ask_yes_no(self, prompt):
        return True # always answer yes
    

class ResultTable(ResultTableBase):
    COLUMNS = [
        Column('marked', ''),
        Column('name', 'Filename'),
        Column('folder_path', 'Directory'),
        Column('size', 'Size (KB)'),
        Column('extension', 'Kind'),
    ]
    DELTA_COLUMNS = {'size', }
    
class DupeGuru(DupeGuruBase):
    METADATA_TO_READ = ['size']
    
    def __init__(self):
        DupeGuruBase.__init__(self, DupeGuruView(), '/tmp')
    
    def _prioritization_categories(self):
        return prioritize.all_categories()
    
    def _create_result_table(self):
        return ResultTable(self)
    

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
    
    def get_display_info(self, group, delta):
        size = self.size
        m = group.get_match_of(self)
        if m and delta:
            r = group.ref
            size -= r.size
        return {
            'name': self.name,
            'folder_path': str(self.folder_path),
            'size': format_size(size, 0, 1, False),
            'extension': self.extension if hasattr(self, 'extension') else '---',
        }
    
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
        def link_gui(gui):
            gui.view = self.make_logger()
            if hasattr(gui, 'columns'): # tables
                gui.columns.view = self.make_logger()
            return gui
        
        TestAppBase.__init__(self)
        make_gui = self.make_gui
        self.app = DupeGuru()
        self.default_parent = self.app
        self.rtable = link_gui(self.app.result_table)
        self.dtree = link_gui(self.app.directory_tree)
        self.dpanel = link_gui(self.app.details_panel)
        self.slabel = link_gui(self.app.stats_label)
        self.pdialog = PrioritizeDialog(self.app)
        link_gui(self.pdialog.category_list)
        link_gui(self.pdialog.criteria_list)
        link_gui(self.pdialog.prioritization_list)
        link_gui(self.app.ignore_list_dialog)
        link_gui(self.app.ignore_list_dialog.ignore_list_table)
    
    #--- Helpers
    def select_pri_criterion(self, name):
        # Select a main prioritize criterion by name instead of by index. Makes tests more
        # maintainable.
        index = self.pdialog.category_list.index(name)
        self.pdialog.category_list.select(index)
    
    def add_pri_criterion(self, name, index):
        self.select_pri_criterion(name)
        self.pdialog.criteria_list.select([index])
        self.pdialog.add_selected()
