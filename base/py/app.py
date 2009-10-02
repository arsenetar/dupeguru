#!/usr/bin/env python
# Created By: Virgil Dupras
# Created On: 2006/11/11
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from __future__ import unicode_literals

import os
import os.path as op
import logging

from hsutil import job, io, files
from hsutil.path import Path
from hsutil.reg import RegistrableApplication, RegistrationRequired
from hsutil.misc import flatten, first
from hsutil.str import escape

from . import directories, results, scanner, export

JOB_SCAN = 'job_scan'
JOB_LOAD = 'job_load'
JOB_MOVE = 'job_move'
JOB_COPY = 'job_copy'
JOB_DELETE = 'job_delete'

class NoScannableFileError(Exception):
    pass

class AllFilesAreRefError(Exception):
    pass

class DupeGuru(RegistrableApplication):
    def __init__(self, data_module, appdata, appid):
        RegistrableApplication.__init__(self, appid)
        self.appdata = appdata
        if not op.exists(self.appdata):
            os.makedirs(self.appdata)
        self.data = data_module
        self.directories = directories.Directories()
        self.results = results.Results(data_module)
        self.scanner = scanner.Scanner()
        self.action_count = 0
        self.last_op_error_count = 0
        self.options = {
            'escape_filter_regexp': True,
            'clean_empty_dirs': False,
        }
    
    def _demo_check(self):
        if self.registered:
            return
        count = self.results.mark_count
        if count + self.action_count > 10:
            raise RegistrationRequired()
        else:
            self.action_count += count
    
    def _do_delete(self, j):
        def op(dupe):
            j.add_progress()
            return self._do_delete_dupe(dupe)
        
        j.start_job(self.results.mark_count)
        self.last_op_error_count = self.results.perform_on_marked(op, True)
    
    def _do_delete_dupe(self, dupe):
        if not io.exists(dupe.path):
            dupe.parent = None
            return True
        self._recycle_dupe(dupe)
        self.clean_empty_dirs(dupe.path[:-1])
        if not io.exists(dupe.path):
            dupe.parent = None
            return True
        logging.warning("Could not send {0} to trash.".format(unicode(dupe.path)))
        return False
    
    def _do_load(self, j):
        self.directories.load_from_file(op.join(self.appdata, 'last_directories.xml'))
        j = j.start_subjob([1, 9])
        self.results.load_from_xml(op.join(self.appdata, 'last_results.xml'), self._get_file, j)
        files = flatten(g[:] for g in self.results.groups)
        for file in j.iter_with_progress(files, 'Reading metadata %d/%d'):
            file._read_all_info(attrnames=self.data.METADATA_TO_READ)
    
    def _get_display_info(self, dupe, group, delta=False):
        if (dupe is None) or (group is None):
            return ['---'] * len(self.data.COLUMNS)
        try:
            return self.data.GetDisplayInfo(dupe, group, delta)
        except Exception as e:
            logging.warning("Exception on GetDisplayInfo for %s: %s", unicode(dupe.path), unicode(e))
            return ['---'] * len(self.data.COLUMNS)
    
    def _get_file(self, str_path):
        p = Path(str_path)
        for d in self.directories:
            if p not in d.path:
                continue
            result = d.find_path(p[d.path:])
            if result is not None:
                return result
    
    @staticmethod
    def _recycle_dupe(dupe):
        raise NotImplementedError()
    
    def _start_job(self, jobid, func):
        # func(j)
        raise NotImplementedError()
    
    def add_directory(self, d):
        try:
            self.directories.add_path(Path(d))
            return 0
        except directories.AlreadyThereError:
            return 1
        except directories.InvalidPathError:
            return 2
    
    def add_to_ignore_list(self, dupe):
        g = self.results.get_group_of_duplicate(dupe)
        for other in g:
            if other is not dupe:
                self.scanner.ignore_list.Ignore(unicode(other.path), unicode(dupe.path))
    
    def apply_filter(self, filter):
        self.results.apply_filter(None)
        if self.options['escape_filter_regexp']:
            filter = escape(filter, '()[]\\.|+?^')
            filter = escape(filter, '*', '.')
        self.results.apply_filter(filter)
    
    def clean_empty_dirs(self, path):
        if self.options['clean_empty_dirs']:
            while files.delete_if_empty(path, ['.DS_Store']):
                path = path[:-1]
    
    def copy_or_move(self, dupe, copy, destination, dest_type):
        """
            copy: True = Copy False = Move
            destination: string.
            dest_type: 0 = right in destination.
                       1 = relative re-creation.
                       2 = absolute re-creation.
        """
        source_path = dupe.path
        location_path = dupe.root.path
        dest_path = Path(destination)
        if dest_type == 2:
            dest_path = dest_path + source_path[1:-1] #Remove drive letter and filename
        elif dest_type == 1:
            dest_path = dest_path + source_path[location_path:-1]
        try:
            if not io.exists(dest_path):
                io.makedirs(dest_path)
            if copy:
                files.copy(source_path, dest_path)
            else:
                files.move(source_path, dest_path)
                self.clean_empty_dirs(source_path[:-1])
        except EnvironmentError as e:
            operation = 'Copy' if copy else 'Move'
            logging.warning('%s operation failed on %s. Error: %s' % (operation, unicode(dupe.path), unicode(e)))
            return False
        return True
    
    def copy_or_move_marked(self, copy, destination, recreate_path):
        def do(j):
            def op(dupe):
                j.add_progress()
                return self.copy_or_move(dupe, copy, destination, recreate_path)
            
            j.start_job(self.results.mark_count)
            self.last_op_error_count = self.results.perform_on_marked(op, not copy)
        
        self._demo_check()
        jobid = JOB_COPY if copy else JOB_MOVE
        self._start_job(jobid, do)
    
    def delete_marked(self):
        self._demo_check()
        self._start_job(JOB_DELETE, self._do_delete)
    
    def export_to_xhtml(self, column_ids):
        column_ids = [colid for colid in column_ids if colid.isdigit()]
        column_ids = map(int, column_ids)
        column_ids.sort()
        colnames = [col['display'] for i, col in enumerate(self.data.COLUMNS) if i in column_ids]
        rows = []
        for group in self.results.groups:
            for dupe in group:
                data = self._get_display_info(dupe, group)
                row = [data[colid] for colid in column_ids]
                row.insert(0, dupe is not group.ref)
                rows.append(row)
        return export.export_to_xhtml(colnames, rows)
    
    def load(self):
        self._start_job(JOB_LOAD, self._do_load)
        self.load_ignore_list()
    
    def load_ignore_list(self):
        p = op.join(self.appdata, 'ignore_list.xml')
        self.scanner.ignore_list.load_from_xml(p)
    
    def make_reference(self, duplicates):
        changed_groups = set()
        for dupe in duplicates:
            g = self.results.get_group_of_duplicate(dupe)
            if g not in changed_groups:
                self.results.make_ref(dupe)
                changed_groups.add(g)
    
    def save(self):
        self.directories.save_to_file(op.join(self.appdata, 'last_directories.xml'))
        self.results.save_to_xml(op.join(self.appdata, 'last_results.xml'))
    
    def save_ignore_list(self):
        p = op.join(self.appdata, 'ignore_list.xml')
        self.scanner.ignore_list.save_to_xml(p)
    
    def start_scanning(self):
        def do(j):
            j.set_progress(0, 'Collecting files to scan')
            files = list(self.directories.get_files())
            logging.info('Scanning %d files' % len(files))
            self.results.groups = self.scanner.GetDupeGroups(files, j)
        
        files = self.directories.get_files()
        first_file = first(files)
        if first_file is None:
            raise NoScannableFileError()
        if first_file.is_ref and all(f.is_ref for f in files):
            raise AllFilesAreRefError()
        self.results.groups = []
        self._start_job(JOB_SCAN, do)
    
    #--- Properties
    @property
    def stat_line(self):
        result = self.results.stat_line
        if self.scanner.discarded_file_count:
            result = '%s (%d discarded)' % (result, self.scanner.discarded_file_count)
        return result
    
