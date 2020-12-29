# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from .markable import Markable
from xml.etree import ElementTree as ET
# TODO: perhaps use regex module for better Unicode support? https://pypi.org/project/regex/
# also https://pypi.org/project/re2/
# TODO update the Result list with newly added regexes if possible
import re
from os import sep
import logging
import functools
from hscommon.util import FileOrPath
from hscommon.plat import ISWINDOWS
import time

default_regexes = [r"^thumbs\.db$",  # Obsolete after WindowsXP
                   r"^desktop\.ini$",  # Windows metadata
                   r"^\.DS_Store$",  # MacOS metadata
                   r"^\.Trash\-.*",  # Linux trash directories
                   r"^\$Recycle\.Bin$",  # Windows
                   r"^\..*",  # Hidden files on Unix-like
                   ]
# These are too broad
forbidden_regexes = [r".*", r"\/.*", r".*\/.*", r".*\\\\.*", r".*\..*"]


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
    """A list of lists holding regular expression strings and the compiled re.Pattern"""

    # Used to filter out directories and files that we would rather avoid scanning.
    # The list() class allows us to preserve item order without too much hassle.
    # The downside is we have to compare strings every time we look for an item in the list
    # since we use regex strings as keys.
    # If _use_union is True, the compiled regexes will be combined into one single
    # Pattern instead of separate Patterns which may or may not give better
    # performance compared to looping through each Pattern individually.

    # ---Override
    def __init__(self, union_regex=True):
        Markable.__init__(self)
        self._use_union = union_regex
        # list([str regex, bool iscompilable, re.error exception, Pattern compiled], ...)
        self._excluded = []
        self._excluded_compiled = set()
        self._dirty = True

    def __iter__(self):
        """Iterate in order."""
        for item in self._excluded:
            regex = item[0]
            yield self.is_marked(regex), regex

    def __contains__(self, item):
        return self.isExcluded(item)

    def __len__(self):
        """Returns the total number of regexes regardless of mark status."""
        return len(self._excluded)

    def __getitem__(self, key):
        """Returns the list item corresponding to key."""
        for item in self._excluded:
            if item[0] == key:
                return item
        raise KeyError(f"Key {key} is not in exclusion list.")

    def __setitem__(self, key, value):
        # TODO if necessary
        pass

    def __delitem__(self, key):
        # TODO if necessary
        pass

    def get_compiled(self, key):
        """Returns the (precompiled) Pattern for key"""
        return self.__getitem__(key)[3]

    def is_markable(self, regex):
        return self._is_markable(regex)

    def _is_markable(self, regex):
        """Return the cached result of "compilable" property"""
        for item in self._excluded:
            if item[0] == regex:
                return item[1]
        return False  # should not be necessary, the regex SHOULD be in there

    def _did_mark(self, regex):
        self._add_compiled(regex)

    def _did_unmark(self, regex):
        self._remove_compiled(regex)

    def _add_compiled(self, regex):
        self._dirty = True
        if self._use_union:
            return
        for item in self._excluded:
            # FIXME probably faster to just rebuild the set from the compiled instead of comparing strings
            if item[0] == regex:
                # no need to test if already present since it's a set()
                self._excluded_compiled.add(item[3])
                break

    def _remove_compiled(self, regex):
        self._dirty = True
        if self._use_union:
            return
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
        """Return the compilation error Exception for regex.
        It should have a "msg" attr."""
        for item in self._excluded:
            if item[0] == regex:
                return item[2]

    def build_compiled_caches(self, union=False):
        if not union:
            self._cached_compiled_files =\
                [x for x in self._excluded_compiled if not has_sep(x.pattern)]
            self._cached_compiled_paths =\
                [x for x in self._excluded_compiled if has_sep(x.pattern)]
            return
        marked_count = [x for marked, x in self if marked]
        # If there is no item, the compiled Pattern will be '' and match everything!
        if not marked_count:
            self._cached_compiled_union_all = []
            self._cached_compiled_union_files = []
            self._cached_compiled_union_paths = []
        else:
            # HACK returned as a tuple to get a free iterator and keep interface
            # the same regardless of whether the client asked for union or not
            self._cached_compiled_union_all =\
                (re.compile('|'.join(marked_count)),)
            files_marked = [x for x in marked_count if not has_sep(x)]
            if not files_marked:
                self._cached_compiled_union_files = tuple()
            else:
                self._cached_compiled_union_files =\
                    (re.compile('|'.join(files_marked)),)
            paths_marked = [x for x in marked_count if has_sep(x)]
            if not paths_marked:
                self._cached_compiled_union_paths = tuple()
            else:
                self._cached_compiled_union_paths =\
                    (re.compile('|'.join(paths_marked)),)

    @property
    def compiled(self):
        """Should be used by other classes to retrieve the up-to-date list of patterns."""
        if self._use_union:
            if self._dirty:
                self.build_compiled_caches(True)
                self._dirty = False
            return self._cached_compiled_union_all
        return self._excluded_compiled

    @property
    def compiled_files(self):
        """When matching against filenames only, we probably won't be seeing any
        directory separator, so we filter out regexes with os.sep in them.
        The interface should be expected to be a generator, even if it returns only
        one item (one Pattern in the union case)."""
        if self._dirty:
            self.build_compiled_caches(True if self._use_union else False)
            self._dirty = False
        return self._cached_compiled_union_files if self._use_union\
            else self._cached_compiled_files

    @property
    def compiled_paths(self):
        """Returns patterns with only separators in them, for more precise filtering."""
        if self._dirty:
            self.build_compiled_caches(True if self._use_union else False)
            self._dirty = False
        return self._cached_compiled_union_paths if self._use_union\
            else self._cached_compiled_paths

    # ---Public
    def add(self, regex, forced=False):
        """This interface should throw exceptions if there is an error during
        regex compilation"""
        if self.isExcluded(regex):
            # This exception should never be ignored
            raise AlreadyThereException()
        if regex in forbidden_regexes:
            raise Exception("Forbidden (dangerous) expression.")

        iscompilable, exception, compiled = self.compile_re(regex)
        if not iscompilable and not forced:
            # This exception can be ignored, but taken into account
            # to avoid adding to compiled set
            raise exception
        else:
            self._do_add(regex, iscompilable, exception, compiled)

    def _do_add(self, regex, iscompilable, exception, compiled):
        # We need to insert at the top
        self._excluded.insert(0, [regex, iscompilable, exception, compiled])

    @property
    def marked_count(self):
        """Returns the number of marked regexes only."""
        return len([x for marked, x in self if marked])

    def isExcluded(self, regex):
        for item in self._excluded:
            if regex == item[0]:
                return True
        return False

    def remove(self, regex):
        for item in self._excluded:
            if item[0] == regex:
                self._excluded.remove(item)
        self._remove_compiled(regex)

    def rename(self, regex, newregex):
        if regex == newregex:
            return
        found = False
        was_marked = False
        is_compilable = False
        for item in self._excluded:
            if item[0] == regex:
                found = True
                was_marked = self.is_marked(regex)
                is_compilable, exception, compiled = self.compile_re(newregex)
                # We overwrite the found entry
                self._excluded[self._excluded.index(item)] =\
                    [newregex, is_compilable, exception, compiled]
                self._remove_compiled(regex)
                break
        if not found:
            return
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
                logging.error(f"Regex \"{regex_string}\" \
loaded from XML was already present in the list.")
                continue
            if exclude_item.get("marked") == "y":
                marked.add(regex_string)

        for item in marked:
            self.mark(item)

    def save_to_xml(self, outfile):
        """Create a XML file that can be used by load_from_xml.
        outfile can be a file object or a filename."""
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
    """Exclusion list holding a set of regular expressions as keys, the compiled
    Pattern, compilation error and compilable boolean as values."""
    # Implemntation around a dictionary instead of a list, which implies
    # to keep the index of each string-key as its sub-element and keep it updated
    # whenever insert/remove is done.

    def __init__(self, union_regex=False):
        Markable.__init__(self)
        self._use_union = union_regex
        # { "regex string":
        #   {
        #       "index": int,
        #       "compilable": bool,
        #       "error": str,
        #       "compiled": Pattern or None
        #   }
        # }
        self._excluded = {}
        self._excluded_compiled = set()
        self._dirty = True

    def __iter__(self):
        """Iterate in order."""
        for regex in ordered_keys(self._excluded):
            yield self.is_marked(regex), regex

    def __getitem__(self, key):
        """Returns the dict item correponding to key"""
        return self._excluded.__getitem__(key)

    def get_compiled(self, key):
        """Returns the compiled item for key"""
        return self.__getitem__(key).get("compiled")

    def is_markable(self, regex):
        return self._is_markable(regex)

    def _is_markable(self, regex):
        """Return the cached result of "compilable" property"""
        exists = self._excluded.get(regex)
        if exists:
            return exists.get("compilable")
        return False

    def _add_compiled(self, regex):
        self._dirty = True
        if self._use_union:
            return
        try:
            self._excluded_compiled.add(self._excluded[regex]["compiled"])
        except Exception as e:
            logging.warning(f"Exception while adding regex {regex} to compiled set: {e}")
            return

    def is_compilable(self, regex):
        """Returns the cached "compilable" value"""
        return self._excluded[regex]["compilable"]

    def error(self, regex):
        """Return the compilation error message for regex string"""
        return self._excluded.get(regex).get("error")

    # ---Public
    def _do_add(self, regex, iscompilable, exception, compiled):
        # We always insert at the top, so index should be 0
        # and other indices should be pushed by one
        for value in self._excluded.values():
            value["index"] += 1
        self._excluded[regex] = {
            "index": 0,
            "compilable": iscompilable,
            "error": exception,
            "compiled": compiled
        }

    def isExcluded(self, regex):
        if regex in self._excluded.keys():
            return True
        return False

    def remove(self, regex):
        old_value = self._excluded.pop(regex)
        # Bring down all indices which where above it
        index = old_value["index"]
        if index == len(self._excluded) - 1:  # we start at 0...
            # Old index was at the end, no need to update other indices
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
        self._excluded[newregex] = {
            "index": previous["index"],
            "compilable": iscompilable,
            "error": error,
            "compiled": compiled
        }
        self._remove_compiled(regex)
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


if ISWINDOWS:
    def has_sep(x):
        return '\\' + sep in x
else:
    def has_sep(x):
        return sep in x
