# Created By: Virgil Dupras
# Created On: 2006/02/23
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import logging
import re
from lxml import etree

from . import engine
from hscommon.job import nulljob
from hscommon.markable import Markable
from hsutil.misc import flatten, nonone
from hsutil.str import format_size
from hsutil.files import FileOrPath

class Results(Markable):
    #---Override
    def __init__(self, data_module):
        super(Results, self).__init__()
        self.__groups = []
        self.__group_of_duplicate = {}
        self.__groups_sort_descriptor = None # This is a tuple (key, asc)
        self.__dupes = None
        self.__dupes_sort_descriptor = None # This is a tuple (key, asc, delta)
        self.__filters = None
        self.__filtered_dupes = None
        self.__filtered_groups = None
        self.__recalculate_stats()
        self.__marked_size = 0
        self.data = data_module
        self.problems = [] # (dupe, error_msg)
        self.is_modified = False
    
    def _did_mark(self, dupe):
        self.__marked_size += dupe.size
    
    def _did_unmark(self, dupe):
        self.__marked_size -= dupe.size
    
    def _get_markable_count(self):
        return self.__total_count
    
    def _is_markable(self, dupe):
        if dupe.is_ref:
            return False
        g = self.get_group_of_duplicate(dupe)
        if not g:
            return False
        if dupe is g.ref:
            return False
        if self.__filtered_dupes and dupe not in self.__filtered_dupes:
            return False
        return True
    
    #---Private
    def __get_dupe_list(self):
        if self.__dupes is None:
            self.__dupes = flatten(group.dupes for group in self.groups)
            if None in self.__dupes:
                # This is debug logging to try to figure out #44
                logging.warning("There is a None value in the Results' dupe list. dupes: %r groups: %r", self.__dupes, self.groups)
            if self.__filtered_dupes:
                self.__dupes = [dupe for dupe in self.__dupes if dupe in self.__filtered_dupes]
            sd = self.__dupes_sort_descriptor
            if sd:
                self.sort_dupes(sd[0], sd[1], sd[2])
        return self.__dupes
    
    def __get_groups(self):
        if self.__filtered_groups is None:
            return self.__groups
        else:
            return self.__filtered_groups
    
    def __get_stat_line(self):
        if self.__filtered_dupes is None:
            mark_count = self.mark_count
            marked_size = self.__marked_size
            total_count = self.__total_count
            total_size = self.__total_size
        else:
            mark_count = len([dupe for dupe in self.__filtered_dupes if self.is_marked(dupe)])
            marked_size = sum(dupe.size for dupe in self.__filtered_dupes if self.is_marked(dupe))
            total_count = len([dupe for dupe in self.__filtered_dupes if self.is_markable(dupe)])
            total_size = sum(dupe.size for dupe in self.__filtered_dupes if self.is_markable(dupe))
        if self.mark_inverted:
            marked_size = self.__total_size - marked_size
        result = '%d / %d (%s / %s) duplicates marked.' % (
            mark_count,
            total_count,
            format_size(marked_size, 2),
            format_size(total_size, 2),
        )
        if self.__filters:
            result += ' filter: %s' % ' --> '.join(self.__filters)
        return result
    
    def __recalculate_stats(self):
        self.__total_size = 0
        self.__total_count = 0
        for group in self.groups:
            markable = [dupe for dupe in group.dupes if self._is_markable(dupe)]
            self.__total_count += len(markable)
            self.__total_size += sum(dupe.size for dupe in markable)
    
    def __set_groups(self, new_groups):
        self.mark_none()
        self.__groups = new_groups
        self.__group_of_duplicate = {}
        for g in self.__groups:
            for dupe in g:
                self.__group_of_duplicate[dupe] = g
                if not hasattr(dupe, 'is_ref'):
                    dupe.is_ref = False
        self.is_modified = True
        old_filters = nonone(self.__filters, [])
        self.apply_filter(None)
        for filter_str in old_filters:
            self.apply_filter(filter_str)
    
    #---Public
    def apply_filter(self, filter_str):
        ''' Applies a filter 'filter_str' to self.groups
        
            When you apply the filter, only  dupes with the filename matching 'filter_str' will be in
            in the results. To cancel the filter, just call apply_filter with 'filter_str' to None, 
            and the results will go back to normal.
            
            If call apply_filter on a filtered results, the filter will be applied 
            *on the filtered results*.
            
            'filter_str' is a string containing a regexp to filter dupes with.
        '''
        if not filter_str:
            self.__filtered_dupes = None
            self.__filtered_groups = None
            self.__filters = None
        else:
            if not self.__filters:
                self.__filters = []
            try:
                filter_re = re.compile(filter_str, re.IGNORECASE)
            except re.error:
                return # don't apply this filter.
            self.__filters.append(filter_str)
            if self.__filtered_dupes is None:
                self.__filtered_dupes = flatten(g[:] for g in self.groups)
            self.__filtered_dupes = set(dupe for dupe in self.__filtered_dupes if filter_re.search(str(dupe.path)))
            filtered_groups = set()
            for dupe in self.__filtered_dupes:
                filtered_groups.add(self.get_group_of_duplicate(dupe))
            self.__filtered_groups = list(filtered_groups)
        self.__recalculate_stats()
        sd = self.__groups_sort_descriptor
        if sd:
            self.sort_groups(sd[0], sd[1])
        self.__dupes = None
    
    def get_group_of_duplicate(self, dupe):
        try:
            return self.__group_of_duplicate[dupe]
        except (TypeError, KeyError):
            return None
    
    is_markable = _is_markable
    
    def load_from_xml(self, infile, get_file, j=nulljob):
        def do_match(ref_file, other_files, group):
            if not other_files:
                return
            for other_file in other_files:
                group.add_match(engine.get_match(ref_file, other_file))
            do_match(other_files[0], other_files[1:], group)
        
        self.apply_filter(None)
        try:
            root = etree.parse(infile).getroot()
        except Exception:
            return
        group_elems = list(root.iterchildren('group'))
        groups = []
        marked = set()
        for group_elem in j.iter_with_progress(group_elems, every=100):
            group = engine.Group()
            dupes = []
            for file_elem in group_elem.iterchildren('file'):
                path = file_elem.get('path')
                words = file_elem.get('words', '')
                if not path:
                    continue
                file = get_file(path)
                if file is None:
                    continue
                file.words = words.split(',')
                file.is_ref = file_elem.get('is_ref') == 'y'
                dupes.append(file)
                if file_elem.get('marked') == 'y':
                    marked.add(file)
            for match_elem in group_elem.iterchildren('match'):
                try:
                    attrs = match_elem.attrib
                    first_file = dupes[int(attrs['first'])]
                    second_file = dupes[int(attrs['second'])]
                    percentage = int(attrs['percentage'])
                    group.add_match(engine.Match(first_file, second_file, percentage))
                except (IndexError, KeyError, ValueError): # Covers missing attr, non-int values and indexes out of bounds
                    pass
            if (not group.matches) and (len(dupes) >= 2):
                do_match(dupes[0], dupes[1:], group)
            group.prioritize(lambda x: dupes.index(x))
            if len(group):
                groups.append(group)    
            j.add_progress()
        self.groups = groups
        for dupe_file in marked:
            self.mark(dupe_file)
        self.is_modified = False
    
    def make_ref(self, dupe):
        g = self.get_group_of_duplicate(dupe)
        r = g.ref
        self._remove_mark_flag(dupe)
        g.switch_ref(dupe);
        if not r.is_ref:
            self.__total_count += 1
            self.__total_size += r.size
        if not dupe.is_ref:
            self.__total_count -= 1
            self.__total_size -= dupe.size
        self.__dupes = None
        self.is_modified = True
    
    def perform_on_marked(self, func, remove_from_results):
        # Performs `func` on all marked dupes. If an EnvironmentError is raised during the call,
        # the problematic dupe is added to self.problems.
        self.problems = []
        to_remove = []
        marked = (dupe for dupe in self.dupes if self.is_marked(dupe))
        for dupe in marked:
            try:
                func(dupe)
                to_remove.append(dupe)
            except EnvironmentError as e:
                self.problems.append((dupe, str(e)))
        if remove_from_results:
            self.remove_duplicates(to_remove)
            self.mark_none()
            for dupe, _ in self.problems:
                self.mark(dupe)
    
    def remove_duplicates(self, dupes):
        '''Remove 'dupes' from their respective group, and remove the group is it ends up empty.
        '''
        affected_groups = set()
        for dupe in dupes:
            group = self.get_group_of_duplicate(dupe)
            if dupe not in group.dupes:
                return
            group.remove_dupe(dupe, False)
            self._remove_mark_flag(dupe)
            self.__total_count -= 1
            self.__total_size -= dupe.size
            if not group:
                self.__groups.remove(group)
                if self.__filtered_groups:
                    self.__filtered_groups.remove(group)
            else:
                affected_groups.add(group)
        for group in affected_groups:
            group.discard_matches()
        self.__dupes = None
        self.is_modified = True
    
    def save_to_xml(self, outfile):
        self.apply_filter(None)
        root = etree.Element('results')
        # writer = XMLGenerator(outfile, 'utf-8')
        for g in self.groups:
            group_elem = etree.SubElement(root, 'group')
            dupe2index = {}
            for index, d in enumerate(g):
                dupe2index[d] = index
                try:
                    words = engine.unpack_fields(d.words)
                except AttributeError:
                    words = ()
                file_elem = etree.SubElement(group_elem, 'file')
                try:
                    file_elem.set('path', str(d.path))
                    file_elem.set('words', ','.join(words))
                except ValueError: # If there's an invalid character, just skip the file
                    file_elem.set('path', '')
                file_elem.set('is_ref', ('y' if d.is_ref else 'n'))
                file_elem.set('marked', ('y' if self.is_marked(d) else 'n'))
            for match in g.matches:
                match_elem = etree.SubElement(group_elem, 'match')
                match_elem.set('first', str(dupe2index[match.first]))
                match_elem.set('second', str(dupe2index[match.second]))
                match_elem.set('percentage', str(int(match.percentage)))
        tree = etree.ElementTree(root)
        with FileOrPath(outfile, 'wb') as fp:
            tree.write(fp, encoding='utf-8')
        self.is_modified = False
    
    def sort_dupes(self, key, asc=True, delta=False):
        if not self.__dupes:
            self.__get_dupe_list()
        self.__dupes.sort(key=lambda d: self.data.GetDupeSortKey(d, lambda: self.get_group_of_duplicate(d), key, delta))
        if not asc:
            self.__dupes.reverse()
        self.__dupes_sort_descriptor = (key,asc,delta)
    
    def sort_groups(self,key,asc=True):
        self.groups.sort(key=lambda g: self.data.GetGroupSortKey(g, key))
        if not asc:
            self.groups.reverse()
        self.__groups_sort_descriptor = (key,asc)
    
    #---Properties
    dupes     = property(__get_dupe_list)
    groups    = property(__get_groups, __set_groups)
    stat_line = property(__get_stat_line)
