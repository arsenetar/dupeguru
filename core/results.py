# Created By: Virgil Dupras
# Created On: 2006/02/23
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

import logging
import re
import os
import os.path as op
from errno import EISDIR, EACCES
from typing import List
from xml.etree import ElementTree as ET

from hscommon.jobprogress.job import nulljob
from hscommon.conflict import get_conflicted_name
from hscommon.util import flatten, nonone, FileOrPath, format_size
from hscommon.trans import tr

from core import engine
from core.fs import File
from core.markable import Markable


class Results(Markable):
    """Manages a collection of duplicate :class:`~core.engine.Group`.

    This class takes care or marking, sorting and filtering duplicate groups.

    .. attribute:: groups

        The list of :class:`~core.engine.Group` contained managed by this instance.

    .. attribute:: dupes

        A list of all duplicates (:class:`~core.fs.File` instances), without ref, contained in the
        currently managed :attr:`groups`.
    """

    # ---Override
    def __init__(self, app):
        Markable.__init__(self)
        self.__groups = []
        self.__group_of_duplicate = {}
        self.__groups_sort_descriptor = None  # This is a tuple (key, asc)
        self.__dupes = None
        self.__dupes_sort_descriptor = None  # This is a tuple (key, asc, delta)
        self.__filters = None
        self.__filtered_dupes = None
        self.__filtered_groups = None
        # Marked references are kept apart from Markable's marks so that Mark All, Invert Marking
        # and marking the selection never mark a reference: only marking that one file does.
        self.__marked_refs = set()
        self.__recalculate_stats()
        self.__marked_size = 0
        self.app = app
        self.problems = []  # (dupe, error_msg)
        self.is_modified = False
        self.refresh_required = False

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

    def mark_all(self):
        if self.__filters:
            self.mark_multiple(self.__filtered_dupes)
        else:
            Markable.mark_all(self)

    def mark_invert(self):
        if self.__filters:
            self.mark_toggle_multiple(self.__filtered_dupes)
        else:
            Markable.mark_invert(self)

    def mark_none(self):
        if self.__filters:
            self.unmark_multiple(self.__filtered_dupes)
            self.__marked_refs -= self.__filtered_dupes
        else:
            Markable.mark_none(self)
            self.__marked_refs = set()

    # ---Private
    def __get_dupe_list(self):
        if self.__dupes is None or self.refresh_required:
            self.__dupes = flatten(group.dupes for group in self.groups)
            self.refresh_required = False
            if None in self.__dupes:
                # This is debug logging to try to figure out #44
                logging.warning(
                    "There is a None value in the Results' dupe list. dupes: %r groups: %r",
                    self.__dupes,
                    self.groups,
                )
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
        result = tr("%d / %d (%s / %s) duplicates marked.") % (
            mark_count,
            total_count,
            format_size(marked_size, 2),
            format_size(total_size, 2),
        )
        marked_refs = self.marked_refs
        if marked_refs:
            result += tr(" Reference files marked: %d (%s).") % (
                len(marked_refs),
                format_size(sum(ref.size for ref in marked_refs), 2),
            )
        if self.__filters:
            result += tr(" filter: %s") % " --> ".join(self.__filters)
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
        self.__marked_refs = set()
        self.__groups = new_groups
        self.__group_of_duplicate = {}
        for g in self.__groups:
            for dupe in g:
                self.__group_of_duplicate[dupe] = g
                if not hasattr(dupe, "is_ref"):
                    dupe.is_ref = False
        self.is_modified = bool(self.__groups)
        old_filters = nonone(self.__filters, [])
        self.apply_filter(None)
        for filter_str in old_filters:
            self.apply_filter(filter_str)

    # ---Public
    def apply_filter(self, filter_str):
        """Applies a filter ``filter_str`` to :attr:`groups`

        When you apply the filter, only  dupes with the filename matching ``filter_str`` will be in
        in the results. To cancel the filter, just call apply_filter with ``filter_str`` to None,
        and the results will go back to normal.

        If call apply_filter on a filtered results, the filter will be applied
        *on the filtered results*.

        :param str filter_str: a string containing a regexp to filter dupes with.
        """
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
                return  # don't apply this filter.
            self.__filters.append(filter_str)
            if self.__filtered_dupes is None:
                self.__filtered_dupes = flatten(g[:] for g in self.groups)
            self.__filtered_dupes = {dupe for dupe in self.__filtered_dupes if filter_re.search(str(dupe.path))}
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
        """Returns :class:`~core.engine.Group` in which ``dupe`` belongs."""
        try:
            return self.__group_of_duplicate[dupe]
        except (TypeError, KeyError):
            return None

    is_markable = _is_markable

    def is_ref_markable(self, file: File) -> bool:
        """Whether ``file`` is a group's reference that can be marked.

        Only with the ``allow_marking_refs`` option on, and never for a file from a reference
        folder (``is_ref``), whose folder state says it must not be deleted.
        """
        if not self.app.options.get("allow_marking_refs", False):
            return False
        if file.is_ref:
            return False
        g = self.get_group_of_duplicate(file)
        if not g or file is not g.ref:
            return False
        if self.__filtered_dupes and file not in self.__filtered_dupes:
            return False
        return True

    def is_ref_marked(self, file: File) -> bool:
        """Whether ``file`` is a marked reference. A mark is valid only while the file is still
        its group's reference."""
        return file in self.__marked_refs and self.is_ref_markable(file)

    def mark_ref(self, file: File) -> bool:
        if not self.is_ref_markable(file):
            return False
        self.__marked_refs.add(file)
        return True

    def unmark_ref(self, file: File) -> bool:
        if file not in self.__marked_refs:
            return False
        self.__marked_refs.discard(file)
        return True

    def forget_moved_ref_marks(self) -> None:
        """Drop the marks of files that are no longer their group's reference.

        Without this, a reference that was marked, lost its position, then got it back, would be
        marked again without anyone having asked for it.
        """
        groups = {f: self.get_group_of_duplicate(f) for f in self.__marked_refs}
        self.__marked_refs = {f for f, g in groups.items() if g is not None and g.ref is f}

    @property
    def marked_refs(self) -> List[File]:
        """The marked references, in :attr:`groups` order."""
        if not self.__marked_refs:
            return []
        return [g.ref for g in self.groups if g.ref is not None and self.is_ref_marked(g.ref)]

    @property
    def marked_file_count(self) -> int:
        """How many files the actions on marked files act on: marked duplicates and references."""
        return self.mark_count + len(self.marked_refs)

    def load_from_xml(self, infile, get_file, j=nulljob):
        """Load results from ``infile``.

        :param infile: a file or path pointing to an XML file created with :meth:`save_to_xml`.
        :param get_file: a function f(path) returning a :class:`~core.fs.File` wrapping the path.
        :param j: A :ref:`job progress instance <jobs>`.
        """

        def do_match(ref_file, other_files, group):
            if not other_files:
                return
            for other_file in other_files:
                group.add_match(engine.get_match(ref_file, other_file))
            do_match(other_files[0], other_files[1:], group)

        self.apply_filter(None)
        root = ET.parse(infile).getroot()
        group_elems = list(root.iter("group"))
        groups = []
        marked = set()
        for group_elem in j.iter_with_progress(group_elems, every=100):
            group = engine.Group()
            dupes = []
            for file_elem in group_elem.iter("file"):
                path = file_elem.get("path")
                words = file_elem.get("words", "")
                if not path:
                    continue
                file = get_file(path)
                if file is None:
                    continue
                file.words = words.split(",")
                file.is_ref = file_elem.get("is_ref") == "y"
                dupes.append(file)
                if file_elem.get("marked") == "y":
                    marked.add(file)
            for match_elem in group_elem.iter("match"):
                try:
                    attrs = match_elem.attrib
                    first_file = dupes[int(attrs["first"])]
                    second_file = dupes[int(attrs["second"])]
                    percentage = int(attrs["percentage"])
                    group.add_match(engine.Match(first_file, second_file, percentage))
                except (IndexError, KeyError, ValueError):
                    # Covers missing attr, non-int values and indexes out of bounds
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
        """Make ``dupe`` take the :attr:`~core.engine.Group.ref` position of its group."""
        g = self.get_group_of_duplicate(dupe)
        r = g.ref
        if not g.switch_ref(dupe):
            return False
        self._remove_mark_flag(dupe)
        self.__marked_refs.discard(r)
        if not r.is_ref:
            self.__total_count += 1
            self.__total_size += r.size
        if not dupe.is_ref:
            self.__total_count -= 1
            self.__total_size -= dupe.size
        self.__dupes = None
        self.is_modified = True
        return True

    def perform_on_marked(self, func, remove_from_results):
        """Performs ``func`` on all marked dupes, then on all marked references.

        If an ``EnvironmentError`` is raised during the call, the problematic dupe is added to
        self.problems.

        :param bool remove_from_results: If true, dupes which had ``func`` applied and didn't cause
                                         any problem.
        """
        self.problems = []
        to_remove = []
        marked_refs = self.marked_refs
        marked = [dupe for dupe in self.dupes if self.is_marked(dupe)] + marked_refs
        for dupe in marked:
            try:
                func(dupe)
                to_remove.append(dupe)
            except (OSError, UnicodeEncodeError) as e:
                self.problems.append((dupe, str(e)))
        if remove_from_results:
            refs = set(marked_refs)
            # The duplicates go first: a reference's removal can dissolve its group.
            self.remove_duplicates([f for f in to_remove if f not in refs])
            self.__remove_refs([f for f in to_remove if f in refs])
            self.mark_none()
            for dupe, _ in self.problems:
                if dupe in refs:
                    self.mark_ref(dupe)
                else:
                    # A duplicate that took the place of a removed reference stays unmarked.
                    self.mark(dupe)

    def __remove_refs(self, refs: List[File]) -> None:
        """Remove references from their groups; the first duplicate of each takes the reference
        position. A group left with a single file is removed."""
        if not refs:
            return
        affected_groups = set()
        for ref in refs:
            group = self.get_group_of_duplicate(ref)
            if group is None or group.ref is not ref:
                continue  # its group went with its last duplicate
            others = group.dupes
            group.remove_dupe(ref, False)
            del self.__group_of_duplicate[ref]
            self.__marked_refs.discard(ref)
            if group:
                self._remove_mark_flag(group.ref)
                affected_groups.add(group)
            else:
                for f in others:
                    del self.__group_of_duplicate[f]
                    self._remove_mark_flag(f)
                self.__groups.remove(group)
                if self.__filtered_groups:
                    self.__filtered_groups.remove(group)
                affected_groups.discard(group)
        for group in affected_groups:
            group.discard_matches()
        self.__recalculate_stats()
        self.__dupes = None
        self.is_modified = bool(self.__groups)

    def remove_duplicates(self, dupes):
        """Remove ``dupes`` from their respective :class:`~core.engine.Group`.

        Also, remove the group from :attr:`groups` if it ends up empty.
        """
        affected_groups = set()
        for dupe in dupes:
            group = self.get_group_of_duplicate(dupe)
            if dupe not in group.dupes:
                return
            ref = group.ref
            group.remove_dupe(dupe, False)
            del self.__group_of_duplicate[dupe]
            self._remove_mark_flag(dupe)
            self.__total_count -= 1
            self.__total_size = max(0, self.__total_size - dupe.size)
            if not group:
                del self.__group_of_duplicate[ref]
                self.__groups.remove(group)
                if self.__filtered_groups:
                    self.__filtered_groups.remove(group)
            else:
                affected_groups.add(group)
        for group in affected_groups:
            group.discard_matches()
        self.__dupes = None
        self.is_modified = bool(self.__groups)

    def save_to_xml(self, outfile):
        """Save results to ``outfile`` in XML.

        :param outfile: file object or path.
        """
        self.apply_filter(None)
        root = ET.Element("results")
        for g in self.groups:
            group_elem = ET.SubElement(root, "group")
            dupe2index = {}
            for index, d in enumerate(g):
                dupe2index[d] = index
                try:
                    words = engine.unpack_fields(d.words)
                except AttributeError:
                    words = ()
                file_elem = ET.SubElement(group_elem, "file")
                try:
                    file_elem.set("path", str(d.path))
                    file_elem.set("words", ",".join(words))
                except ValueError:  # If there's an invalid character, just skip the file
                    file_elem.set("path", "")
                file_elem.set("is_ref", ("y" if d.is_ref else "n"))
                file_elem.set("marked", ("y" if self.is_marked(d) else "n"))
            for match in g.matches:
                match_elem = ET.SubElement(group_elem, "match")
                match_elem.set("first", str(dupe2index[match.first]))
                match_elem.set("second", str(dupe2index[match.second]))
                match_elem.set("percentage", str(int(match.percentage)))
        tree = ET.ElementTree(root)

        def do_write(outfile):
            with FileOrPath(outfile, "wb") as fp:
                tree.write(fp, encoding="utf-8")

        try:
            do_write(outfile)
        except OSError as e:
            # If our OSError is because dest is already a directory, we want to handle that. 21 is
            # the code we get on OS X and Linux (EISDIR), 13 is what we get on Windows (EACCES).
            if e.errno in (EISDIR, EACCES):
                p = str(outfile)
                dirname, basename = op.split(p)
                otherfiles = os.listdir(dirname)
                newname = get_conflicted_name(otherfiles, basename)
                do_write(op.join(dirname, newname))
            else:
                raise
        self.is_modified = False

    def sort_dupes(self, key, asc=True, delta=False):
        """Sort :attr:`dupes` according to ``key``.

        :param str key: key attribute name to sort with.
        :param bool asc: If false, sorting is reversed.
        :param bool delta: If true, sorting occurs using :ref:`delta values <deltavalues>`.
        """
        if not self.__dupes:
            self.__get_dupe_list()
        self.__dupes.sort(
            key=lambda d: self.app._get_dupe_sort_key(d, lambda: self.get_group_of_duplicate(d), key, delta),
            reverse=not asc,
        )
        self.__dupes_sort_descriptor = (key, asc, delta)

    def sort_groups(self, key, asc=True):
        """Sort :attr:`groups` according to ``key``.

        The :attr:`~core.engine.Group.ref` of each group is used to extract values for sorting.

        :param str key: key attribute name to sort with.
        :param bool asc: If false, sorting is reversed.
        """
        self.groups.sort(key=lambda g: self.app._get_group_sort_key(g, key), reverse=not asc)
        self.__groups_sort_descriptor = (key, asc)

    # ---Properties
    dupes = property(__get_dupe_list)
    groups = property(__get_groups, __set_groups)
    stat_line = property(__get_stat_line)
