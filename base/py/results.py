# Created By: Virgil Dupras
# Created On: 2006/02/23
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import logging
import re
from xml.sax import handler, make_parser, SAXException
from xml.sax.saxutils import XMLGenerator
from xml.sax.xmlreader import AttributesImpl

from . import engine
from hsutil.job import nulljob
from hsutil.markable import Markable
from hsutil.misc import flatten, cond, nonone
from hsutil.str import format_size
from hsutil.files import open_if_filename

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
            self.__filters.append(filter_str)
            filter_re = re.compile(filter_str, re.IGNORECASE)
            if self.__filtered_dupes is None:
                self.__filtered_dupes = flatten(g[:] for g in self.groups)
            self.__filtered_dupes = set(dupe for dupe in self.__filtered_dupes if filter_re.search(dupe.name))
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
        self.apply_filter(None)
        handler = _ResultsHandler(get_file)
        try:
            parser = make_parser()
        except Exception as e:
            # This special handling is to try to figure out the cause of #47
            # We don't silently return, because we want the user to send error report.
            logging.exception(e)
            try:
                import xml.parsers.expat
                logging.warning('importing xml.parsers.expat went ok, WTF?')
            except Exception as e:
                # This log should give a little more details about the cause of this all
                logging.exception(e)
                raise
            raise
        parser.setContentHandler(handler)
        try:
            infile, must_close = open_if_filename(infile)
        except IOError:
            return
        BUFSIZE = 1024 * 1024 # 1mb buffer
        infile.seek(0, 2)
        j.start_job(infile.tell() // BUFSIZE)
        infile.seek(0, 0)
        try:
            while True:
                data = infile.read(BUFSIZE)
                if not data:
                    break
                parser.feed(data)
                j.add_progress()
        except SAXException:
            return
        self.groups = handler.groups
        for dupe_file in handler.marked:
            self.mark(dupe_file)
    
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
    
    def perform_on_marked(self, func, remove_from_results):
        problems = []
        for d in self.dupes:
            if self.is_marked(d) and (not func(d)):
                problems.append(d)
        if remove_from_results:
            to_remove = [d for d in self.dupes if self.is_marked(d) and (d not in problems)]
            self.remove_duplicates(to_remove)
            self.mark_none()
            for d in problems:
                self.mark(d)
        return len(problems)
    
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
            group.clean_matches()
        self.__dupes = None
    
    def save_to_xml(self, outfile):
        self.apply_filter(None)
        outfile, must_close = open_if_filename(outfile, 'wb')
        writer = XMLGenerator(outfile, 'utf-8')
        writer.startDocument()
        empty_attrs = AttributesImpl({})
        writer.startElement('results', empty_attrs)
        for g in self.groups:
            writer.startElement('group', empty_attrs)
            dupe2index = {}
            for index, d in enumerate(g):
                dupe2index[d] = index
                try:
                    words = engine.unpack_fields(d.words)
                except AttributeError:
                    words = ()
                attrs = AttributesImpl({
                    'path': unicode(d.path),
                    'is_ref': cond(d.is_ref, 'y', 'n'),
                    'words': ','.join(words),
                    'marked': cond(self.is_marked(d), 'y', 'n')
                })
                writer.startElement('file', attrs)
                writer.endElement('file')
            for match in g.matches:
                attrs = AttributesImpl({
                    'first': str(dupe2index[match.first]),
                    'second': str(dupe2index[match.second]),
                    'percentage': str(int(match.percentage)),
                })
                writer.startElement('match', attrs)
                writer.endElement('match')
            writer.endElement('group')
        writer.endElement('results')
        writer.endDocument()
        if must_close:
            outfile.close()
    
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

class _ResultsHandler(handler.ContentHandler):
    def __init__(self, get_file):
        self.group = None
        self.dupes = None
        self.marked = set()
        self.groups = []
        self.get_file = get_file
    
    def startElement(self, name, attrs):
        if name == 'group':
            self.group = engine.Group()
            self.dupes = []
            return
        if (name == 'file') and (self.group is not None):
            if not (('path' in attrs) and ('words' in attrs)):
                return
            path = attrs['path']
            file = self.get_file(path)
            if file is None:
                return
            file.words = attrs['words'].split(',')
            file.is_ref = attrs.get('is_ref') == 'y'
            self.dupes.append(file)
            if attrs.get('marked') == 'y':
                self.marked.add(file)
        if (name == 'match') and (self.group is not None):
            try:
                first_file = self.dupes[int(attrs['first'])]
                second_file = self.dupes[int(attrs['second'])]
                percentage = int(attrs['percentage'])
                self.group.add_match(engine.Match(first_file, second_file, percentage))
            except (IndexError, KeyError, ValueError): # Covers missing attr, non-int values and indexes out of bounds
                pass
    
    def endElement(self, name):
        def do_match(ref_file, other_files, group):
            if not other_files:
                return
            for other_file in other_files:
                group.add_match(engine.get_match(ref_file, other_file))
            do_match(other_files[0], other_files[1:], group)
        
        if name == 'group':
            group = self.group
            self.group = None
            dupes = self.dupes
            self.dupes = []
            if group is None:
                return
            if len(dupes) < 2:
                return
            if not group.matches: # <match> elements not present, do it manually, without %
                do_match(dupes[0], dupes[1:], group)
            group.prioritize(lambda x: dupes.index(x))
            self.groups.append(group)
    
