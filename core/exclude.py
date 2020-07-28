# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from .markable import Markable
from xml.etree import ElementTree as ET
from hscommon.util import FileOrPath


class ExcludeList(Markable):
    """Exclude list of regular expression strings to filter out directories
    and files that we want to avoid scanning."""

    # ---Override
    def __init__(self, app):
        Markable.__init__(self)
        self.app = app
        self._excluded = []  # set of strings
        self._count = 0

    def __iter__(self):
        for regex in self._excluded:
            yield self.is_marked(regex), regex

    def __len__(self):
        return self._count

    def _is_markable(self, row):
        return True

    # ---Public
    def add(self, regex):
        self._excluded.insert(0, regex)
        self._count = len(self._excluded)

    def isExcluded(self, regex):
        if regex in self._excluded:
            return True
        return False

    def clear(self):
        self._excluded = []
        self._count = 0

    def remove(self, regex):
        return self._excluded.remove(regex)

    def rename(self, regex, newregex):
        if regex not in self._excluded:
            return
        marked = self.is_marked(regex)
        index = self._excluded.index(regex)
        self._excluded[index] = newregex
        if marked:
            # Not marked by default when added
            self.mark(self._excluded[index])

    def change_index(self, regex, new_index):
        item = self._excluded.pop(regex)
        self._excluded.insert(new_index, item)

    def load_from_xml(self, infile):
        """Loads the ignore list from a XML created with save_to_xml.

        infile can be a file object or a filename.
        """
        try:
            root = ET.parse(infile).getroot()
        except Exception as e:
            print(f"Error while loading {infile}: {e}")
            return
        marked = set()
        exclude_elems = (e for e in root if e.tag == "exclude")
        for exclude_item in exclude_elems:
            regex_string = exclude_item.get("regex")
            if not regex_string:
                continue
            self.add(regex_string)
            if exclude_item.get("marked") == "y":
                marked.add(regex_string)
            for item in marked:
                # this adds item to the Markable "marked" set
                self.mark(item)

    def save_to_xml(self, outfile):
        """Create a XML file that can be used by load_from_xml.

        outfile can be a file object or a filename.
        """
        root = ET.Element("exclude_list")
        for regex in self._excluded:
            exclude_node = ET.SubElement(root, "exclude")
            exclude_node.set("regex", str(regex))
            exclude_node.set("marked", ("y" if self.is_marked(regex) else "n"))
        tree = ET.ElementTree(root)
        with FileOrPath(outfile, "wb") as fp:
            tree.write(fp, encoding="utf-8")
