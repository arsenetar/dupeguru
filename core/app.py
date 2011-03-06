# Created By: Virgil Dupras
# Created On: 2006/11/11
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import os
import os.path as op
import logging
import subprocess
import re

from send2trash import send2trash
from hscommon import io
from hscommon.reg import RegistrableApplication
from hscommon.notify import Broadcaster
from hscommon.path import Path
from hscommon.conflict import smart_move, smart_copy
from hscommon.util import delete_if_empty, first, escape, nonone
from hscommon.trans import tr

from . import directories, results, scanner, export, fs

JOB_SCAN = 'job_scan'
JOB_LOAD = 'job_load'
JOB_MOVE = 'job_move'
JOB_COPY = 'job_copy'
JOB_DELETE = 'job_delete'

HAD_FIRST_LAUNCH_PREFERENCE = 'HadFirstLaunch'
DEBUG_MODE_PREFERENCE = 'DebugMode'

class NoScannableFileError(Exception):
    pass

class DestType:
    Direct = 0
    Relative = 1
    Absolute = 2

class DupeGuru(RegistrableApplication, Broadcaster):
    def __init__(self, data_module, appdata):
        if self.get_default(DEBUG_MODE_PREFERENCE, False):
            logging.getLogger().setLevel(logging.DEBUG)
            logging.debug("Debug mode enabled")
        RegistrableApplication.__init__(self, appid=1)
        Broadcaster.__init__(self)
        self.is_first_run = not self.get_default(HAD_FIRST_LAUNCH_PREFERENCE, False)
        if self.is_first_run:
            self.set_default(HAD_FIRST_LAUNCH_PREFERENCE, True)
        self.appdata = appdata
        if not op.exists(self.appdata):
            os.makedirs(self.appdata)
        self.data = data_module
        self.directories = directories.Directories()
        self.results = results.Results(data_module)
        self.scanner = scanner.Scanner()
        self.options = {
            'escape_filter_regexp': True,
            'clean_empty_dirs': False,
            'ignore_hardlink_matches': False,
        }
        self.selected_dupes = []
    
    #--- Private
    def _do_delete(self, j, replace_with_hardlinks):
        def op(dupe):
            j.add_progress()
            return self._do_delete_dupe(dupe, replace_with_hardlinks)
        
        j.start_job(self.results.mark_count)
        self.results.perform_on_marked(op, True)
    
    def _do_delete_dupe(self, dupe, replace_with_hardlinks):
        if not io.exists(dupe.path):
            return
        send2trash(str(dupe.path)) # Raises OSError when there's a problem
        if replace_with_hardlinks:
            group = self.results.get_group_of_duplicate(dupe)
            ref = group.ref
            os.link(str(ref.path), str(dupe.path))
        self.clean_empty_dirs(dupe.path[:-1])
    
    def _get_display_info(self, dupe, group, delta=False):
        if (dupe is None) or (group is None):
            return ['---'] * len(self.data.COLUMNS)
        try:
            return self.data.GetDisplayInfo(dupe, group, delta)
        except Exception as e:
            logging.warning("Exception on GetDisplayInfo for %s: %s", str(dupe.path), str(e))
            return ['---'] * len(self.data.COLUMNS)
    
    def _get_file(self, str_path):
        path = Path(str_path)
        f = fs.get_file(path, self.directories.fileclasses)    
        if f is None:
            return None
        try:
            f._read_all_info(attrnames=self.data.METADATA_TO_READ)
            return f
        except EnvironmentError:
            return None
    
    def _results_changed(self):
        self.selected_dupes = [d for d in self.selected_dupes
            if self.results.get_group_of_duplicate(d) is not None]
        self.notify('results_changed')
    
    def _job_completed(self, jobid):
        # Must be called by subclasses when they detect that an async job is completed.
        if jobid == JOB_SCAN:
            self._results_changed()
        elif jobid in {JOB_LOAD, JOB_MOVE, JOB_DELETE}:
            self._results_changed()
        
        if jobid in {JOB_COPY, JOB_MOVE, JOB_DELETE}:
            self.notify('problems_changed')
    
    @staticmethod
    def _open_path(path):
        raise NotImplementedError()
    
    @staticmethod
    def _reveal_path(path):
        raise NotImplementedError()
    
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
    
    def _start_job(self, jobid, func, *args):
        # func(j, *args)
        raise NotImplementedError()
    
    def _get_default(self, key_name, fallback_value=None):
        raise NotImplementedError()
    
    def _set_default(self, key_name, value):
        raise NotImplementedError()
    
    def _show_extra_fairware_reminder(self):
        raise NotImplementedError()
    
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
        for dupe in dupes:
            g = self.results.get_group_of_duplicate(dupe)
            for other in g:
                if other is not dupe:
                    self.scanner.ignore_list.Ignore(str(other.path), str(dupe.path))
        self.remove_duplicates(dupes)
    
    def apply_filter(self, filter):
        self.results.apply_filter(None)
        if self.options['escape_filter_regexp']:
            filter = escape(filter, set('()[]\\.|+?^'))
            filter = escape(filter, '*', '.')
        self.results.apply_filter(filter)
        self._results_changed()
    
    def show_extra_fairware_reminder_if_needed(self):
        if self.results.mark_count > 100 and self.should_show_fairware_reminder:
            self._show_extra_fairware_reminder()
    
    def clean_empty_dirs(self, path):
        if self.options['clean_empty_dirs']:
            while delete_if_empty(path, ['.DS_Store']):
                path = path[:-1]
    
    def copy_or_move(self, dupe, copy, destination, dest_type):
        """
            copy: True = Copy False = Move
            destination: string.
            dest_type: DestType constants
        """
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
        # Raises an EnvironmentError if there's a problem
        if copy:
            smart_copy(source_path, dest_path)
        else:
            smart_move(source_path, dest_path)
            self.clean_empty_dirs(source_path[:-1])
    
    def copy_or_move_marked(self, copy, destination, recreate_path):
        def do(j):
            def op(dupe):
                j.add_progress()
                self.copy_or_move(dupe, copy, destination, recreate_path)
            
            j.start_job(self.results.mark_count)
            self.results.perform_on_marked(op, not copy)
        
        self.show_extra_fairware_reminder_if_needed()
        jobid = JOB_COPY if copy else JOB_MOVE
        self._start_job(jobid, do)
    
    def delete_marked(self, replace_with_hardlinks=False):
        self.show_extra_fairware_reminder_if_needed()
        self._start_job(JOB_DELETE, self._do_delete, replace_with_hardlinks)
    
    def export_to_xhtml(self, column_ids):
        column_ids = [colid for colid in column_ids if colid.isdigit()]
        column_ids = list(map(int, column_ids))
        column_ids.sort()
        colnames = [col.display for i, col in enumerate(self.data.COLUMNS) if i in column_ids]
        rows = []
        for group in self.results.groups:
            for dupe in group:
                data = self._get_display_info(dupe, group)
                row = [data[colid] for colid in column_ids]
                row.insert(0, dupe is not group.ref)
                rows.append(row)
        return export.export_to_xhtml(colnames, rows)
    
    def invoke_command(self, cmd):
        """Calls command `cmd` with %d and %r placeholders replaced.
        
        Using the current selection, %d is replaced with the currently selected dupe and %r is
        replaced with that dupe's ref file. If there's no selection, the command is not invoked.
        If the dupe is a ref, %d and %r will be the same.
        """
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
    
    def load_from(self, filename):
        def do(j):
            self.results.load_from_xml(filename, self._get_file, j)
        self._start_job(JOB_LOAD, do)
    
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
            self._open_path(self.selected_dupes[0].path)
    
    def purge_ignore_list(self):
        self.scanner.ignore_list.Filter(lambda f,s:op.exists(f) and op.exists(s))
    
    def remove_directory(self,index):
        try:
            del self.directories[index]
            self.notify('directories_changed')
        except IndexError:
            pass
    
    def remove_duplicates(self, duplicates):
        self.results.remove_duplicates(self.without_ref(duplicates))
        self.notify('results_changed_but_keep_selection')
    
    def remove_marked(self):
        self.results.perform_on_marked(lambda x:None, True)
        self._results_changed()
    
    def remove_selected(self):
        self.remove_duplicates(self.selected_dupes)
    
    def rename_selected(self, newname):
        try:
            d = self.selected_dupes[0]
            d.rename(newname)
            return True
        except (IndexError, fs.FSError) as e:
            logging.warning("dupeGuru Warning: %s" % str(e))
        return False
    
    def reveal_selected(self):
        if self.selected_dupes:
            self._reveal_path(self.selected_dupes[0].path)
    
    def save(self):
        if not op.exists(self.appdata):
            os.makedirs(self.appdata)
        self.directories.save_to_file(op.join(self.appdata, 'last_directories.xml'))
        p = op.join(self.appdata, 'ignore_list.xml')
        self.scanner.ignore_list.save_to_xml(p)
    
    def save_as(self, filename):
        self.results.save_to_xml(filename)
    
    def start_scanning(self):
        def do(j):
            j.set_progress(0, tr("Collecting files to scan"))
            files = list(self.directories.get_files())
            if self.options['ignore_hardlink_matches']:
                files = self._remove_hardlink_dupes(files)
            logging.info('Scanning %d files' % len(files))
            self.results.groups = self.scanner.GetDupeGroups(files, j)
        
        if not self.directories.has_any_file():
            raise NoScannableFileError()
        self.results.groups = []
        self._results_changed()
        self._start_job(JOB_SCAN, do)
    
    def toggle_selected_mark_state(self):
        for dupe in self.selected_dupes:
            self.results.mark_toggle(dupe)
        self.notify('marking_changed')
    
    def without_ref(self, dupes):
        return [dupe for dupe in dupes if self.results.get_group_of_duplicate(dupe).ref is not dupe]
    
    def get_default(self, key, fallback_value=None):
        result = nonone(self._get_default(key), fallback_value)
        if fallback_value is not None and not isinstance(result, type(fallback_value)):
            # we don't want to end up with garbage values from the prefs
            try:
                result = type(fallback_value)(result)
            except Exception:
                result = fallback_value
        return result
    
    def set_default(self, key, value):
        self._set_default(key, value)
    
    #--- Properties
    @property
    def stat_line(self):
        result = self.results.stat_line
        if self.scanner.discarded_file_count:
            result = tr("%s (%d discarded)") % (result, self.scanner.discarded_file_count)
        return result
    
