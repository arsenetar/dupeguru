# Created By: Virgil Dupras
# Created On: 2006/11/11
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import os
import os.path as op
import logging
import subprocess
import re
import time

from send2trash import send2trash
from hscommon import io
from hscommon.reg import RegistrableApplication
from hscommon.notify import Broadcaster
from hscommon.path import Path
from hscommon.conflict import smart_move, smart_copy
from hscommon.util import (delete_if_empty, first, escape, nonone, format_time_decimal, allsame,
    rem_file_ext)
from hscommon.trans import tr

from . import directories, results, scanner, export, fs
from .gui.details_panel import DetailsPanel
from .gui.directory_tree import DirectoryTree
from .gui.ignore_list_dialog import IgnoreListDialog
from .gui.problem_dialog import ProblemDialog
from .gui.stats_label import StatsLabel

HAD_FIRST_LAUNCH_PREFERENCE = 'HadFirstLaunch'
DEBUG_MODE_PREFERENCE = 'DebugMode'

MSG_NO_MARKED_DUPES = tr("There are no marked duplicates. Nothing has been done.")
MSG_NO_SELECTED_DUPES = tr("There are no selected duplicates. Nothing has been done.")

class DestType:
    Direct = 0
    Relative = 1
    Absolute = 2

class JobType:
    Scan = 'job_scan'
    Load = 'job_load'
    Move = 'job_move'
    Copy = 'job_copy'
    Delete = 'job_delete'

def format_timestamp(t, delta):
    if delta:
        return format_time_decimal(t)
    else:
        if t > 0:
            return time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(t))
        else:
            return '---'

def format_words(w):
    def do_format(w):
        if isinstance(w, list):
            return '(%s)' % ', '.join(do_format(item) for item in w)
        else:
            return w.replace('\n', ' ')
    
    return ', '.join(do_format(item) for item in w)

def format_perc(p):
    return "%0.0f" % p

def format_dupe_count(c):
    return str(c) if c else '---'

def cmp_value(dupe, attrname):
    if attrname == 'name':
        value = rem_file_ext(dupe.name)
    else:
        value = getattr(dupe, attrname, '')
    return value.lower() if isinstance(value, str) else value

class DupeGuru(RegistrableApplication, Broadcaster):
    #--- View interface
    # open_path(path)
    # reveal_path(path)
    # start_job(jobid, func, args=()) ( func(j, *args) )
    # ask_yes_no(prompt) --> bool
    # show_results_window()
    # show_problem_dialog()
    # select_dest_folder(prompt: str) --> str
    
    # in fairware prompts, we don't mention the edition, it's too long.
    PROMPT_NAME = "dupeGuru"
    DEMO_LIMITATION = tr("will only be able to delete, move or copy 10 duplicates at once")
    
    def __init__(self, view, appdata):
        if view.get_default(DEBUG_MODE_PREFERENCE):
            logging.getLogger().setLevel(logging.DEBUG)
            logging.debug("Debug mode enabled")
        RegistrableApplication.__init__(self, view, appid=1)
        Broadcaster.__init__(self)
        self.appdata = appdata
        if not op.exists(self.appdata):
            os.makedirs(self.appdata)
        self.directories = directories.Directories()
        self.results = results.Results(self)
        self.scanner = scanner.Scanner()
        self.options = {
            'escape_filter_regexp': True,
            'clean_empty_dirs': False,
            'ignore_hardlink_matches': False,
            'copymove_dest_type': DestType.Relative,
        }
        self.selected_dupes = []
        self.details_panel = DetailsPanel(self)
        self.directory_tree = DirectoryTree(self)
        self.problem_dialog = ProblemDialog(self)
        self.ignore_list_dialog = IgnoreListDialog(self)
        self.stats_label = StatsLabel(self)
        self.result_table = self._create_result_table()
        children = [self.result_table, self.directory_tree, self.stats_label, self.details_panel]
        for child in children:
            child.connect()
    
    #--- Virtual
    def _get_display_info(self, dupe, group, delta):
        raise NotImplementedError()
    
    def _prioritization_categories(self):
        raise NotImplementedError()
    
    def _create_result_table(self):
        raise NotImplementedError()
    
    #--- Private
    def _get_dupe_sort_key(self, dupe, get_group, key, delta):
        if key == 'percentage':
            m = get_group().get_match_of(dupe)
            return m.percentage
        if key == 'dupe_count':
            return 0
        if key == 'marked':
            return self.results.is_marked(dupe)
        r = cmp_value(dupe, key)
        if delta and (key in self.result_table.DELTA_COLUMNS):
            r -= cmp_value(get_group().ref, key)
        return r
    
    def _get_group_sort_key(self, group, key):
        if key == 'percentage':
            return group.percentage
        if key == 'dupe_count':
            return len(group)
        if key == 'marked':
            return len([dupe for dupe in group.dupes if self.results.is_marked(dupe)])
        return cmp_value(group.ref, key)
    
    def _do_delete(self, j, replace_with_hardlinks):
        def op(dupe):
            j.add_progress()
            return self._do_delete_dupe(dupe, replace_with_hardlinks)
        
        j.start_job(self.results.mark_count)
        self.results.perform_on_marked(op, True)
    
    def _do_delete_dupe(self, dupe, replace_with_hardlinks):
        if not io.exists(dupe.path):
            return
        logging.debug("Sending '%s' to trash", dupe.path)
        send2trash(str(dupe.path)) # Raises OSError when there's a problem
        if replace_with_hardlinks:
            group = self.results.get_group_of_duplicate(dupe)
            ref = group.ref
            os.link(str(ref.path), str(dupe.path))
        self.clean_empty_dirs(dupe.path[:-1])
    
    def _create_file(self, path):
        # We add fs.Folder to fileclasses in case the file we're loading contains folder paths.
        return fs.get_file(path, self.directories.fileclasses + [fs.Folder])
    
    def _get_file(self, str_path):
        path = Path(str_path)
        f = self._create_file(path)
        if f is None:
            return None
        try:
            f._read_all_info(attrnames=self.METADATA_TO_READ)
            return f
        except EnvironmentError:
            return None
    
    def _results_changed(self):
        self.selected_dupes = [d for d in self.selected_dupes
            if self.results.get_group_of_duplicate(d) is not None]
        self.notify('results_changed')
    
    def _job_completed(self, jobid, exc):
        # Must be called by subclasses when they detect that an async job is completed. If an
        # exception was raised during the job, `exc` will be set. Return True when the error was
        # handled. If we return False when exc is set, a the exception will be re-raised.
        if exc is not None:
            return False # We don't handle any exception in here
        if jobid == JobType.Scan:
            self._results_changed()
            if not self.results.groups:
                self.view.show_message(tr("No duplicates found."))
            else:
                self.view.show_results_window()
        if jobid in {JobType.Load, JobType.Move, JobType.Delete}:
            self._results_changed()
        if jobid == JobType.Load:
            self.view.show_results_window()
        if jobid in {JobType.Copy, JobType.Move, JobType.Delete}:
            if self.results.problems:
                self.problem_dialog.refresh()
                self.view.show_problem_dialog()
            else:
                msg = {
                    JobType.Copy: tr("All marked files were copied sucessfully."),
                    JobType.Move: tr("All marked files were moved sucessfully."),
                    JobType.Delete: tr("All marked files were sucessfully sent to Trash."),
                }[jobid]
                self.view.show_message(msg)
    
    @staticmethod
    def _remove_hardlink_dupes(files):
        seen_inodes = set()
        result = []
        for file in files:
            try:
                inode = io.stat(file.path).st_ino
            except OSError:
                # The file was probably deleted or something
                continue
            if inode not in seen_inodes:
                seen_inodes.add(inode)
                result.append(file)
        return result
    
    def _select_dupes(self, dupes):
        if dupes == self.selected_dupes:
            return
        self.selected_dupes = dupes
        self.notify('dupes_selected')
    
    def _check_demo(self):
        if self.should_apply_demo_limitation and self.results.mark_count > 10:
            msg = tr("You cannot delete, move or copy more than 10 duplicates at once in demo mode.")
            self.view.show_message(msg)
            return False
        return True
            
    #--- Public
    def add_directory(self, d):
        try:
            self.directories.add_path(Path(d))
            self.notify('directories_changed')
            return 0
        except directories.AlreadyThereError:
            return 1
        except directories.InvalidPathError:
            return 2
    
    def add_selected_to_ignore_list(self):
        dupes = self.without_ref(self.selected_dupes)
        if not dupes:
            self.view.show_message(MSG_NO_SELECTED_DUPES)
            return
        msg = tr("All selected %d matches are going to be ignored in all subsequent scans. Continue?")
        if not self.view.ask_yes_no(msg % len(dupes)):
            return
        for dupe in dupes:
            g = self.results.get_group_of_duplicate(dupe)
            for other in g:
                if other is not dupe:
                    self.scanner.ignore_list.Ignore(str(other.path), str(dupe.path))
        self.remove_duplicates(dupes)
        self.ignore_list_dialog.refresh()
    
    def apply_filter(self, filter):
        self.results.apply_filter(None)
        if self.options['escape_filter_regexp']:
            filter = escape(filter, set('()[]\\.|+?^'))
            filter = escape(filter, '*', '.')
        self.results.apply_filter(filter)
        self._results_changed()
    
    def clean_empty_dirs(self, path):
        if self.options['clean_empty_dirs']:
            while delete_if_empty(path, ['.DS_Store']):
                path = path[:-1]
    
    def copy_or_move(self, dupe, copy: bool, destination: str, dest_type: DestType):
        source_path = dupe.path
        location_path = first(p for p in self.directories if dupe.path in p)
        dest_path = Path(destination)
        if dest_type in {DestType.Relative, DestType.Absolute}:
            # no filename, no windows drive letter
            source_base = source_path.remove_drive_letter()[:-1]
            if dest_type == DestType.Relative:
                source_base = source_base[location_path:]
            dest_path = dest_path + source_base
        if not io.exists(dest_path):
            io.makedirs(dest_path)
        # Add filename to dest_path. For file move/copy, it's not required, but for folders, yes.
        dest_path = dest_path + source_path[-1]
        logging.debug("Copy/Move operation from '%s' to '%s'", source_path, dest_path)
        # Raises an EnvironmentError if there's a problem
        if copy:
            smart_copy(source_path, dest_path)
        else:
            smart_move(source_path, dest_path)
            self.clean_empty_dirs(source_path[:-1])
    
    def copy_or_move_marked(self, copy):
        def do(j):
            def op(dupe):
                j.add_progress()
                self.copy_or_move(dupe, copy, destination, desttype)
            
            j.start_job(self.results.mark_count)
            self.results.perform_on_marked(op, not copy)
        
        if not self._check_demo():
            return
        if not self.results.mark_count:
            self.view.show_message(MSG_NO_MARKED_DUPES)
            return
        opname = tr("copy") if copy else tr("move")
        prompt = tr("Select a directory to {} marked files to").format(opname)
        destination = self.view.select_dest_folder(prompt)
        if destination:
            desttype = self.options['copymove_dest_type']
            jobid = JobType.Copy if copy else JobType.Move
            self.view.start_job(jobid, do)
    
    def delete_marked(self, replace_with_hardlinks=False):
        if not self._check_demo():
            return
        if not self.results.mark_count:
            self.view.show_message(MSG_NO_MARKED_DUPES)
            return
        if replace_with_hardlinks:
            msg = tr("You are about to send %d files to Trash (and hardlink them afterwards). Continue?")
        else:
            msg = tr("You are about to send %d files to Trash. Continue?")
        if not self.view.ask_yes_no(msg % self.results.mark_count):
            return
        self.view.start_job(JobType.Delete, self._do_delete, args=[replace_with_hardlinks])
    
    def export_to_xhtml(self):
        columns = [col for col in self.result_table.columns.ordered_columns
            if col.visible and col.name != 'marked']
        colnames = [col.display for col in columns]
        rows = []
        for group in self.results.groups:
            for dupe in group:
                data = self.get_display_info(dupe, group)
                row = [data[col.name] for col in columns]
                row.insert(0, dupe is not group.ref)
                rows.append(row)
        return export.export_to_xhtml(colnames, rows)
    
    def get_display_info(self, dupe, group, delta=False):
        def empty_data():
            return {c.name: '---' for c in self.result_table.COLUMNS[1:]}
        if (dupe is None) or (group is None):
            return empty_data()
        try:
            return self._get_display_info(dupe, group, delta)
        except Exception as e:
            logging.warning("Exception on GetDisplayInfo for %s: %s", str(dupe.path), str(e))
            return empty_data()
    
    def invoke_custom_command(self):
        """Calls command in 'CustomCommand' pref with %d and %r placeholders replaced.
        
        Using the current selection, %d is replaced with the currently selected dupe and %r is
        replaced with that dupe's ref file. If there's no selection, the command is not invoked.
        If the dupe is a ref, %d and %r will be the same.
        """
        cmd = self.view.get_default('CustomCommand')
        if not cmd:
            msg = tr("You have no custom command set up. Set it up in your preferences.")
            self.view.show_message(msg)
            return
        if not self.selected_dupes:
            return
        dupe = self.selected_dupes[0]
        group = self.results.get_group_of_duplicate(dupe)
        ref = group.ref
        cmd = cmd.replace('%d', str(dupe.path))
        cmd = cmd.replace('%r', str(ref.path))
        match = re.match(r'"([^"]+)"(.*)', cmd)
        if match is not None:
            # This code here is because subprocess. Popen doesn't seem to accept, under Windows,
            # executable paths with spaces in it, *even* when they're enclosed in "". So this is
            # a workaround to make the damn thing work.
            exepath, args = match.groups()
            path, exename = op.split(exepath)
            subprocess.Popen(exename + args, shell=True, cwd=path)
        else:
            subprocess.Popen(cmd, shell=True)
    
    def load(self):
        self.directories.load_from_file(op.join(self.appdata, 'last_directories.xml'))
        self.notify('directories_changed')
        p = op.join(self.appdata, 'ignore_list.xml')
        self.scanner.ignore_list.load_from_xml(p)
        self.ignore_list_dialog.refresh()
    
    def load_from(self, filename):
        def do(j):
            self.results.load_from_xml(filename, self._get_file, j)
        self.view.start_job(JobType.Load, do)
    
    def make_selected_reference(self):
        dupes = self.without_ref(self.selected_dupes)
        changed_groups = set()
        for dupe in dupes:
            g = self.results.get_group_of_duplicate(dupe)
            if g not in changed_groups:
                self.results.make_ref(dupe)
                changed_groups.add(g)
        self.notify('results_changed_but_keep_selection')
    
    def mark_all(self):
        self.results.mark_all()
        self.notify('marking_changed')
    
    def mark_none(self):
        self.results.mark_none()
        self.notify('marking_changed')
    
    def mark_invert(self):
        self.results.mark_invert()
        self.notify('marking_changed')
    
    def mark_dupe(self, dupe, marked):
        if marked:
            self.results.mark(dupe)
        else:
            self.results.unmark(dupe)
        self.notify('marking_changed')
    
    def open_selected(self):
        if self.selected_dupes:
            self.view.open_path(self.selected_dupes[0].path)
    
    def purge_ignore_list(self):
        self.scanner.ignore_list.Filter(lambda f,s:op.exists(f) and op.exists(s))
        self.ignore_list_dialog.refresh()
    
    def remove_directories(self, indexes):
        try:
            indexes = sorted(indexes, reverse=True)
            for index in indexes:
                del self.directories[index]
            self.notify('directories_changed')
        except IndexError:
            pass
    
    def remove_duplicates(self, duplicates):
        self.results.remove_duplicates(self.without_ref(duplicates))
        self.notify('results_changed_but_keep_selection')
    
    def remove_marked(self):
        if not self.results.mark_count:
            self.view.show_message(MSG_NO_MARKED_DUPES)
            return
        msg = tr("You are about to remove %d files from results. Continue?") 
        if not self.view.ask_yes_no(msg % self.results.mark_count):
            return
        self.results.perform_on_marked(lambda x:None, True)
        self._results_changed()
    
    def remove_selected(self):
        dupes = self.without_ref(self.selected_dupes)
        if not dupes:
            self.view.show_message(MSG_NO_SELECTED_DUPES)
            return
        msg = tr("You are about to remove %d files from results. Continue?") 
        if not self.view.ask_yes_no(msg % len(dupes)):
            return
        self.remove_duplicates(dupes)
    
    def rename_selected(self, newname):
        try:
            d = self.selected_dupes[0]
            d.rename(newname)
            return True
        except (IndexError, fs.FSError) as e:
            logging.warning("dupeGuru Warning: %s" % str(e))
        return False
    
    def reprioritize_groups(self, sort_key):
        for group in self.results.groups:
            group.prioritize(key_func=sort_key)
        self._results_changed()
    
    def reveal_selected(self):
        if self.selected_dupes:
            self.view.reveal_path(self.selected_dupes[0].path)
    
    def save(self):
        if not op.exists(self.appdata):
            os.makedirs(self.appdata)
        self.directories.save_to_file(op.join(self.appdata, 'last_directories.xml'))
        p = op.join(self.appdata, 'ignore_list.xml')
        self.scanner.ignore_list.save_to_xml(p)
        self.notify('save_session')
    
    def save_as(self, filename):
        self.results.save_to_xml(filename)
    
    def start_scanning(self):
        def do(j):
            j.set_progress(0, tr("Collecting files to scan"))
            if self.scanner.scan_type == scanner.ScanType.Folders:
                files = list(self.directories.get_folders(j))
            else:
                files = list(self.directories.get_files(j))
            if self.options['ignore_hardlink_matches']:
                files = self._remove_hardlink_dupes(files)
            logging.info('Scanning %d files' % len(files))
            self.results.groups = self.scanner.get_dupe_groups(files, j)
        
        if not self.directories.has_any_file():
            self.view.show_message(tr("The selected directories contain no scannable file."))
            return
        self.results.groups = []
        self._results_changed()
        self.view.start_job(JobType.Scan, do)
    
    def toggle_selected_mark_state(self):
        selected = self.without_ref(self.selected_dupes)
        if not selected:
            return
        if allsame(self.results.is_marked(d) for d in selected):
            markfunc = self.results.mark_toggle
        else:
            markfunc = self.results.mark
        for dupe in selected:
            markfunc(dupe)
        self.notify('marking_changed')
    
    def without_ref(self, dupes):
        return [dupe for dupe in dupes if self.results.get_group_of_duplicate(dupe).ref is not dupe]
    
    def get_default(self, key, fallback_value=None):
        result = nonone(self.view.get_default(key), fallback_value)
        if fallback_value is not None and not isinstance(result, type(fallback_value)):
            # we don't want to end up with garbage values from the prefs
            try:
                result = type(fallback_value)(result)
            except Exception:
                result = fallback_value
        return result
    
    def set_default(self, key, value):
        self.view.set_default(key, value)
    
    #--- Properties
    @property
    def stat_line(self):
        result = self.results.stat_line
        if self.scanner.discarded_file_count:
            result = tr("%s (%d discarded)") % (result, self.scanner.discarded_file_count)
        return result
    
