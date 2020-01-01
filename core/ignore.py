# Created By: Virgil Dupras
# Created On: 2006/05/02
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from xml.etree import ElementTree as ET

from hscommon.util import FileOrPath


class IgnoreList:
    """An ignore list implementation that is iterable, filterable and exportable to XML.

    Call Ignore to add an ignore list entry, and AreIgnore to check if 2 items are in the list.
    When iterated, 2 sized tuples will be returned, the tuples containing 2 items ignored together.
    """

    # ---Override
    def __init__(self):
        self._ignored = {}
        self._count = 0

    def __iter__(self):
        for first, seconds in self._ignored.items():
            for second in seconds:
                yield (first, second)

    def __len__(self):
        return self._count

    # ---Public
    def AreIgnored(self, first, second):
        def do_check(first, second):
            try:
                matches = self._ignored[first]
                return second in matches
            except KeyError:
                return False

        return do_check(first, second) or do_check(second, first)

    def Clear(self):
        self._ignored = {}
        self._count = 0

    def Filter(self, func):
        """Applies a filter on all ignored items, and remove all matches where func(first,second)
        doesn't return True.
        """
        filtered = IgnoreList()
        for first, second in self:
            if func(first, second):
                filtered.Ignore(first, second)
        self._ignored = filtered._ignored
        self._count = filtered._count

    def Ignore(self, first, second):
        if self.AreIgnored(first, second):
            return
        try:
            matches = self._ignored[first]
            matches.add(second)
        except KeyError:
            try:
                matches = self._ignored[second]
                matches.add(first)
            except KeyError:
                matches = set()
                matches.add(second)
                self._ignored[first] = matches
        self._count += 1

    def remove(self, first, second):
        def inner(first, second):
            try:
                matches = self._ignored[first]
                if second in matches:
                    matches.discard(second)
                    if not matches:
                        del self._ignored[first]
                    self._count -= 1
                    return True
                else:
                    return False
            except KeyError:
                return False

        if not inner(first, second):
            if not inner(second, first):
                raise ValueError()

    def load_from_xml(self, infile):
        """Loads the ignore list from a XML created with save_to_xml.

        infile can be a file object or a filename.
        """
        try:
            root = ET.parse(infile).getroot()
        except Exception:
            return
        file_elems = (e for e in root if e.tag == "file")
        for fn in file_elems:
            file_path = fn.get("path")
            if not file_path:
                continue
            subfile_elems = (e for e in fn if e.tag == "file")
            for sfn in subfile_elems:
                subfile_path = sfn.get("path")
                if subfile_path:
                    self.Ignore(file_path, subfile_path)

    def save_to_xml(self, outfile):
        """Create a XML file that can be used by load_from_xml.

        outfile can be a file object or a filename.
        """
        root = ET.Element("ignore_list")
        for filename, subfiles in self._ignored.items():
            file_node = ET.SubElement(root, "file")
            file_node.set("path", filename)
            for subfilename in subfiles:
                subfile_node = ET.SubElement(file_node, "file")
                subfile_node.set("path", subfilename)
        tree = ET.ElementTree(root)
        with FileOrPath(outfile, "wb") as fp:
            tree.write(fp, encoding="utf-8")
