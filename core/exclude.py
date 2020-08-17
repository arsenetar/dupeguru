# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from .markable import Markable
from xml.etree import ElementTree as ET
import re
from os import sep
import logging
import functools
from hscommon.util import FileOrPath
import time

default_regexes = [r".*thumbs", r"\.DS.Store", r"\.Trash", r".*Trash-Bin"]
forbidden_regexes = [r".*", r"\/.*", r".*\/.*"]


def timer(func):
    @functools.wraps(func)
    def wrapper_timer(*args):
        start = time.perf_counter_ns()
        value = func(*args)
        end = time.perf_counter_ns()
        print(f"DEBUG: func {func.__name__!r} took {end - start} ns.")
        return value
    return wrapper_timer


def memoize(func):
    func.cache = dict()

    @functools.wraps(func)
    def _memoize(*args):
        if args not in func.cache:
            func.cache[args] = func(*args)
        return func.cache[args]
    return _memoize


class AlreadyThereException(Exception):
    """Expression already in the list"""
    def __init__(self, arg="Expression is already in excluded list."):
        super().__init__(arg)


class ExcludeList(Markable):
    """Exclude list of regular expression strings to filter out directories
    and files that we want to avoid scanning.
    The list() class allows us to preserve item order without too much hassle.
    The downside is we have to compare strings every time we look for an item in the list
    since we use regex strings as keys.
    [regex:str, compilable:bool, error:Exception, compiled:Pattern])
    """

    # ---Override
    def __init__(self):
        Markable.__init__(self)
        self._excluded = []
        self._count = 0
        self._excluded_compiled = set()

    def __debug_test(self):
        self.test_regexes = [
            r".*Recycle\.Bin$", r"denyme.*", r".*denyme", r".*/test/denyme*",
            r".*/test/*denyme", r"denyme", r".*\/\..*", r"^\..*"]
        for regex in self.test_regexes:
            try:
                self.add(regex)
            except Exception as e:
                print(f"Exception loading test regex {regex}: {e}")
                continue
            try:
                self.mark(regex)
            except Exception as e:
                print(f"Exception marking test regex {regex}: {e}")

    def __iter__(self):
        """Iterate in order."""
        for item in self._excluded:
            regex = item[0]
            yield self.is_marked(regex), regex

    def __len__(self):
        return self._count

    def is_markable(self, regex):
        return self._is_markable(regex)

    def _is_markable(self, regex):
        """Return the cached result of "compilable" property"""
        # FIXME save result of compilation via memoization
        # return self._excluded.get(regex)[0]
        for item in self._excluded:
            if item[0] == regex:
                return item[1]
        return False  # FIXME should not be needed

    def _did_mark(self, regex):
        for item in self._excluded:
            if item[0] == regex:
                # no need to test if already present since it's a set()
                self._excluded_compiled.add(item[3])

    def _did_unmark(self, regex):
        self._remove_compiled(regex)

    def _remove_compiled(self, regex):
        for item in self._excluded_compiled:
            if regex in item.pattern:
                self._excluded_compiled.remove(item)
                break

    # @timer
    @memoize
    def _do_compile(self, expr):
        try:
            return re.compile(expr)
        except Exception as e:
            raise(e)

    # @timer
    # @memoize  # probably not worth memoizing this one if we memoize the above
    def compile_re(self, regex):
        compiled = None
        try:
            compiled = self._do_compile(regex)
        except Exception as e:
            return False, e, compiled
        return True, None, compiled

    def error(self, regex):
        """Return the compilation error Exception for regex. It should have a "msg" attr."""
        for item in self._excluded:
            if item[0] == regex:
                return item[2]

    @property
    def compiled(self):
        """Should be used by other classes to retrieve the up-to-date list of patterns."""
        return self._excluded_compiled

    @property
    def compiled_files(self):
        """Should be used by other classes to retrieve the up-to-date list of patterns
        for files only."""
        return [compiled_pattern for compiled_pattern in self.compiled if sep not in compiled_pattern.pattern]

    # ---Public
    def add(self, regex, forced=False):
        """This interface should throw exceptions if there is an error during regex compilation"""
        if self.isExcluded(regex):
            # This exception should never be ignored
            raise AlreadyThereException()
        if regex in forbidden_regexes:
            raise Exception("Forbidden (dangerous) expression.")

        iscompilable, exception, compiled = self.compile_re(regex)
        if not iscompilable and not forced:
            # This exception can be ignored, but taken into account to avoid adding to compiled set
            raise exception
        else:
            self._do_add(regex, iscompilable, exception, compiled)

    def _do_add(self, regex, iscompilable, exception, compiled):
        # We need to insert at the top
        self._excluded.insert(0, [regex, iscompilable, exception, compiled])
        self._count = len(self._excluded)

    def isExcluded(self, regex):
        for item in self._excluded:
            if regex == item[0]:
                return True
        return False

    def clear(self):
        self._excluded = []
        self._count = 0

    def remove(self, regex):
        for item in self._excluded:
            if item[0] == regex:
                self._excluded.remove(item)
        self._remove_compiled(regex)

    def rename(self, regex, newregex):
        # if regex not in self._excluded or regex == newregex:
        #     return
        if regex == newregex:
            return
        found = False
        for item in self._excluded:
            if regex == item[0]:
                found = True
                break
        if not found:
            return

        was_marked = self.is_marked(regex)
        is_compilable, exception, compiled = self.compile_re(newregex)
        for item in self._excluded:
            if item[0] == regex:
                # We overwrite the found entry
                self._excluded[self._excluded.index(item)] =\
                    [newregex, is_compilable, exception, compiled]
        if is_compilable and was_marked:
            # Not marked by default when added, add it back
            self.mark(newregex)

    # def change_index(self, regex, new_index):
    # """Internal list must be a list, not dict."""
    #     item = self._excluded.pop(regex)
    #     self._excluded.insert(new_index, item)

    def restore_defaults(self):
        for _, regex in self:
            if regex not in default_regexes:
                self.unmark(regex)
        for default_regex in default_regexes:
            if not self.isExcluded(default_regex):
                self.add(default_regex)
            self.mark(default_regex)

    def load_from_xml(self, infile):
        """Loads the ignore list from a XML created with save_to_xml.

        infile can be a file object or a filename.
        """
        try:
            root = ET.parse(infile).getroot()
        except Exception as e:
            logging.warning(f"Error while loading {infile}: {e}")
            self.restore_defaults()
            self.__debug_test()
            return e

        marked = set()
        exclude_elems = (e for e in root if e.tag == "exclude")
        for exclude_item in exclude_elems:
            regex_string = exclude_item.get("regex")
            if not regex_string:
                continue
            try:
                # "forced" avoids compilation exceptions and adds anyway
                self.add(regex_string, forced=True)
            except AlreadyThereException:
                logging.error(f"Regex \"{regex_string}\" loaded from XML was already present in the list.")
                continue
            if exclude_item.get("marked") == "y":
                marked.add(regex_string)

        for item in marked:
            self.mark(item)
        self.__debug_test()

    def save_to_xml(self, outfile):
        """Create a XML file that can be used by load_from_xml.

        outfile can be a file object or a filename.
        """
        root = ET.Element("exclude_list")
        # reversed in order to keep order of entries when reloading from xml later
        for item in reversed(self._excluded):
            exclude_node = ET.SubElement(root, "exclude")
            exclude_node.set("regex", str(item[0]))
            exclude_node.set("marked", ("y" if self.is_marked(item[0]) else "n"))
        tree = ET.ElementTree(root)
        with FileOrPath(outfile, "wb") as fp:
            tree.write(fp, encoding="utf-8")


class ExcludeDict(ExcludeList):
    """Version implemented around a dictionary instead of a list, which implies
    to keep the index of each string-key as its sub-element and keep it updated
    whenever insert/remove is done."""

    def __init__(self):
        Markable.__init__(self)
        # { "regex": { "index": int, "compilable": bool, "error": str, "compiled": Pattern or None}}
        # Note: "compilable" key should only be updated on add / rename
        self._excluded = {}
        self._count = 0
        self._excluded_compiled = set()

    def __iter__(self):
        """Iterate in order."""
        for regex in ordered_keys(self._excluded):
            yield self.is_marked(regex), regex

    def __len__(self):
        return self._count

    def is_markable(self, regex):
        return self._is_markable(regex)

    def _is_markable(self, regex):
        """Return the cached result of "compilable" property"""
        exists = self._excluded.get(regex)
        if exists:
            return exists.get("compilable")
        return False

    def _did_mark(self, regex):
        # self._excluded[regex][0] = True  # is compilable
        try:
            self._excluded_compiled.add(self._excluded[regex]["compiled"])
        except Exception as e:
            print(f"Exception while adding regex {regex} to compiled set: {e}")
            return

    def _did_unmark(self, regex):
        self._remove_compiled(regex)

    def is_compilable(self, regex):
        """Returns the cached "compilable" value"""
        return self._excluded[regex]["compilable"]

    def error(self, regex):
        """Return the compilation error message for regex string"""
        return self._excluded.get(regex).get("error")

    @property
    def compiled(self):
        """Should be used by other classes to retrieve the up-to-date list of patterns."""
        return self._excluded_compiled

    @property
    def compiled_files(self):
        """Should be used by other classes to retrieve the up-to-date list of patterns
        for files only."""
        return [compiled_pattern for compiled_pattern in self.compiled if sep not in compiled_pattern.pattern]

    # ---Public
    def _do_add(self, regex, iscompilable, exception, compiled):
        # We always insert at the top, so index should be 0 and other indices should be pushed by one
        for value in self._excluded.values():
            value["index"] += 1
        self._excluded[regex] = {"index": 0, "compilable": iscompilable, "error": exception, "compiled": compiled}
        self._count = len(self._excluded)

    def isExcluded(self, regex):
        if regex in self._excluded.keys():
            return True
        return False

    def clear(self):
        self._excluded = {}
        self._count = 0

    def remove(self, regex):
        old_value = self._excluded.pop(regex)
        # Bring down all indices which where above it
        index = old_value["index"]
        if index == len(self._excluded):
            self._remove_compiled(regex)
            return

        for value in self._excluded.values():
            if value.get("index") > old_value["index"]:
                value["index"] -= 1
        self._remove_compiled(regex)

    def rename(self, regex, newregex):
        if regex == newregex or regex not in self._excluded.keys():
            return
        was_marked = self.is_marked(regex)
        previous = self._excluded.pop(regex)
        iscompilable, error, compiled = self.compile_re(newregex)
        self._excluded[newregex] = {"index": previous["index"], "compilable": iscompilable, "error": error, "compiled": compiled}
        if was_marked and iscompilable:
            self.mark(newregex)

    def save_to_xml(self, outfile):
        """Create a XML file that can be used by load_from_xml.

        outfile can be a file object or a filename.
        """
        root = ET.Element("exclude_list")
        # reversed in order to keep order of entries when reloading from xml later
        reversed_list = []
        for key in ordered_keys(self._excluded):
            reversed_list.append(key)
        for item in reversed(reversed_list):
            exclude_node = ET.SubElement(root, "exclude")
            exclude_node.set("regex", str(item))
            exclude_node.set("marked", ("y" if self.is_marked(item) else "n"))
        tree = ET.ElementTree(root)
        with FileOrPath(outfile, "wb") as fp:
            tree.write(fp, encoding="utf-8")


def ordered_keys(_dict):
    """Returns an iterator over the keys of dictionary sorted by "index" key"""
    if not len(_dict):
        return
    list_of_items = []
    for item in _dict.items():
        list_of_items.append(item)
    list_of_items.sort(key=lambda x: x[1].get("index"))
    for item in list_of_items:
        yield item[0]
