# Created By: Virgil Dupras
# Created On: 2006/01/29
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

import difflib
import itertools
import logging
import string
from collections import defaultdict, namedtuple
from unicodedata import normalize

from hscommon.util import flatten, multi_replace
from hscommon.trans import tr
from hscommon.jobprogress import job

(
    WEIGHT_WORDS,
    MATCH_SIMILAR_WORDS,
    NO_FIELD_ORDER,
) = range(3)

JOB_REFRESH_RATE = 100
PROGRESS_MESSAGE = tr("%d matches found from %d groups")


def getwords(s):
    # We decompose the string so that ascii letters with accents can be part of the word.
    s = normalize("NFD", s)
    s = multi_replace(s, "-_&+():;\\[]{}.,<>/?~!@#$*", " ").lower()
    # logging.debug(f"DEBUG chars for: {s}\n"
    #               f"{[c for c in s if ord(c) != 32]}\n"
    #               f"{[ord(c) for c in s if ord(c) != 32]}")
    # HACK We shouldn't ignore non-ascii characters altogether. Any Unicode char
    # above common european characters that cannot be "sanitized" (ie. stripped
    # of their accents, etc.) are preserved as is. The arbitrary limit is
    # obtained from this one: ord("\u037e") GREEK QUESTION MARK
    s = "".join(
        c
        for c in s
        if (ord(c) <= 894 and c in string.ascii_letters + string.digits + string.whitespace) or ord(c) > 894
    )
    return [_f for _f in s.split(" ") if _f]  # remove empty elements


def getfields(s):
    fields = [getwords(field) for field in s.split(" - ")]
    return [_f for _f in fields if _f]


def unpack_fields(fields):
    result = []
    for field in fields:
        if isinstance(field, list):
            result += field
        else:
            result.append(field)
    return result


def compare(first, second, flags=()):
    """Returns the % of words that match between ``first`` and ``second``

    The result is a ``int`` in the range 0..100.
    ``first`` and ``second`` can be either a string or a list (of words).
    """
    if not (first and second):
        return 0
    if any(isinstance(element, list) for element in first):
        return compare_fields(first, second, flags)
    second = second[:]  # We must use a copy of second because we remove items from it
    match_similar = MATCH_SIMILAR_WORDS in flags
    weight_words = WEIGHT_WORDS in flags
    joined = first + second
    total_count = sum(len(word) for word in joined) if weight_words else len(joined)
    match_count = 0
    in_order = True
    for word in first:
        if match_similar and (word not in second):
            similar = difflib.get_close_matches(word, second, 1, 0.8)
            if similar:
                word = similar[0]
        if word in second:
            if second[0] != word:
                in_order = False
            second.remove(word)
            match_count += len(word) if weight_words else 1
    result = round(((match_count * 2) / total_count) * 100)
    if (result == 100) and (not in_order):
        result = 99  # We cannot consider a match exact unless the ordering is the same
    return result


def compare_fields(first, second, flags=()):
    """Returns the score for the lowest matching :ref:`fields`.

    ``first`` and ``second`` must be lists of lists of string. Each sub-list is then compared with
    :func:`compare`.
    """
    if len(first) != len(second):
        return 0
    if NO_FIELD_ORDER in flags:
        results = []
        # We don't want to remove field directly in the list. We must work on a copy.
        second = second[:]
        for field1 in first:
            max_score = 0
            matched_field = None
            for field2 in second:
                r = compare(field1, field2, flags)
                if r > max_score:
                    max_score = r
                    matched_field = field2
            results.append(max_score)
            if matched_field:
                second.remove(matched_field)
    else:
        results = [compare(field1, field2, flags) for field1, field2 in zip(first, second)]
    return min(results) if results else 0


def build_word_dict(objects, j=job.nulljob):
    """Returns a dict of objects mapped by their words.

    objects must have a ``words`` attribute being a list of strings or a list of lists of strings
    (:ref:`fields`).

    The result will be a dict with words as keys, lists of objects as values.
    """
    result = defaultdict(set)
    for object in j.iter_with_progress(objects, "Prepared %d/%d files", JOB_REFRESH_RATE):
        for word in unpack_fields(object.words):
            result[word].add(object)
    return result


def merge_similar_words(word_dict):
    """Take all keys in ``word_dict`` that are similar, and merge them together.

    ``word_dict`` has been built with :func:`build_word_dict`. Similarity is computed with Python's
    ``difflib.get_close_matches()``, which computes the number of edits that are necessary to make
    a word equal to the other.
    """
    keys = list(word_dict.keys())
    keys.sort(key=len)  # we want the shortest word to stay
    while keys:
        key = keys.pop(0)
        similars = difflib.get_close_matches(key, keys, 100, 0.8)
        if not similars:
            continue
        objects = word_dict[key]
        for similar in similars:
            objects |= word_dict[similar]
            del word_dict[similar]
            keys.remove(similar)


def reduce_common_words(word_dict, threshold):
    """Remove all objects from ``word_dict`` values where the object count >= ``threshold``

    ``word_dict`` has been built with :func:`build_word_dict`.

    The exception to this removal are the objects where all the words of the object are common.
    Because if we remove them, we will miss some duplicates!
    """
    uncommon_words = set(word for word, objects in word_dict.items() if len(objects) < threshold)
    for word, objects in list(word_dict.items()):
        if len(objects) < threshold:
            continue
        reduced = set()
        for o in objects:
            if not any(w in uncommon_words for w in unpack_fields(o.words)):
                reduced.add(o)
        if reduced:
            word_dict[word] = reduced
        else:
            del word_dict[word]


# Writing docstrings in a namedtuple is tricky. From Python 3.3, it's possible to set __doc__, but
# some research allowed me to find a more elegant solution, which is what is done here. See
# http://stackoverflow.com/questions/1606436/adding-docstrings-to-namedtuples-in-python


class Match(namedtuple("Match", "first second percentage")):
    """Represents a match between two :class:`~core.fs.File`.

    Regarless of the matching method, when two files are determined to match, a Match pair is created,
    which holds, of course, the two matched files, but also their match "level".

    .. attribute:: first

        first file of the pair.

    .. attribute:: second

        second file of the pair.

    .. attribute:: percentage

        their match level according to the scan method which found the match. int from 1 to 100. For
        exact scan methods, such as Contents scans, this will always be 100.
    """

    __slots__ = ()


def get_match(first, second, flags=()):
    # it is assumed here that first and second both have a "words" attribute
    percentage = compare(first.words, second.words, flags)
    return Match(first, second, percentage)


def getmatches(
    objects,
    min_match_percentage=0,
    match_similar_words=False,
    weight_words=False,
    no_field_order=False,
    j=job.nulljob,
):
    """Returns a list of :class:`Match` within ``objects`` after fuzzily matching their words.

    :param objects: List of :class:`~core.fs.File` to match.
    :param int min_match_percentage: minimum % of words that have to match.
    :param bool match_similar_words: make similar words (see :func:`merge_similar_words`) match.
    :param bool weight_words: longer words are worth more in match % computations.
    :param bool no_field_order: match :ref:`fields` regardless of their order.
    :param j: A :ref:`job progress instance <jobs>`.
    """
    COMMON_WORD_THRESHOLD = 50
    LIMIT = 5000000
    j = j.start_subjob(2)
    sj = j.start_subjob(2)
    for o in objects:
        if not hasattr(o, "words"):
            o.words = getwords(o.name)
    word_dict = build_word_dict(objects, sj)
    reduce_common_words(word_dict, COMMON_WORD_THRESHOLD)
    if match_similar_words:
        merge_similar_words(word_dict)
    match_flags = []
    if weight_words:
        match_flags.append(WEIGHT_WORDS)
    if match_similar_words:
        match_flags.append(MATCH_SIMILAR_WORDS)
    if no_field_order:
        match_flags.append(NO_FIELD_ORDER)
    j.start_job(len(word_dict), PROGRESS_MESSAGE % (0, 0))
    compared = defaultdict(set)
    result = []
    try:
        word_count = 0
        # This whole 'popping' thing is there to avoid taking too much memory at the same time.
        while word_dict:
            items = word_dict.popitem()[1]
            while items:
                ref = items.pop()
                compared_already = compared[ref]
                to_compare = items - compared_already
                compared_already |= to_compare
                for other in to_compare:
                    m = get_match(ref, other, match_flags)
                    if m.percentage >= min_match_percentage:
                        result.append(m)
                        if len(result) >= LIMIT:
                            return result
            word_count += 1
            j.add_progress(desc=PROGRESS_MESSAGE % (len(result), word_count))
    except MemoryError:
        # This is the place where the memory usage is at its peak during the scan.
        # Just continue the process with an incomplete list of matches.
        del compared  # This should give us enough room to call logging.
        logging.warning("Memory Overflow. Matches: %d. Word dict: %d" % (len(result), len(word_dict)))
        return result
    return result


def getmatches_by_contents(files, bigsize=0, j=job.nulljob):
    """Returns a list of :class:`Match` within ``files`` if their contents is the same.

    :param bigsize: The size in bytes over which we consider files big enough to
                    justify taking samples of the file for hashing. If 0, compute digest as usual.
    :param j: A :ref:`job progress instance <jobs>`.
    """
    size2files = defaultdict(set)
    for f in files:
        size2files[f.size].add(f)
    del files
    possible_matches = [files for files in size2files.values() if len(files) > 1]
    del size2files
    result = []
    j.start_job(len(possible_matches), PROGRESS_MESSAGE % (0, 0))
    group_count = 0
    for group in possible_matches:
        for first, second in itertools.combinations(group, 2):
            if first.is_ref and second.is_ref:
                continue  # Don't spend time comparing two ref pics together.
            if first.size == 0 and second.size == 0:
                # skip hashing for zero length files
                result.append(Match(first, second, 100))
                continue
            if first.digest_partial == second.digest_partial:
                if bigsize > 0 and first.size > bigsize:
                    if first.digest_samples == second.digest_samples:
                        result.append(Match(first, second, 100))
                else:
                    if first.digest == second.digest:
                        result.append(Match(first, second, 100))
        group_count += 1
        j.add_progress(desc=PROGRESS_MESSAGE % (len(result), group_count))
    return result


class Group:
    """A group of :class:`~core.fs.File` that match together.

    This manages match pairs into groups and ensures that all files in the group match to each
    other.

    .. attribute:: ref

        The "reference" file, which is the file among the group that isn't going to be deleted.

    .. attribute:: ordered

        Ordered list of duplicates in the group (including the :attr:`ref`).

    .. attribute:: unordered

        Set duplicates in the group (including the :attr:`ref`).

    .. attribute:: dupes

        An ordered list of the group's duplicate, without :attr:`ref`. Equivalent to
        ``ordered[1:]``

    .. attribute:: percentage

        Average match percentage of match pairs containing :attr:`ref`.
    """

    # ---Override
    def __init__(self):
        self._clear()

    def __contains__(self, item):
        return item in self.unordered

    def __getitem__(self, key):
        return self.ordered.__getitem__(key)

    def __iter__(self):
        return iter(self.ordered)

    def __len__(self):
        return len(self.ordered)

    # ---Private
    def _clear(self):
        self._percentage = None
        self._matches_for_ref = None
        self.matches = set()
        self.candidates = defaultdict(set)
        self.ordered = []
        self.unordered = set()

    def _get_matches_for_ref(self):
        if self._matches_for_ref is None:
            ref = self.ref
            self._matches_for_ref = [match for match in self.matches if ref in match]
        return self._matches_for_ref

    # ---Public
    def add_match(self, match):
        """Adds ``match`` to internal match list and possibly add duplicates to the group.

        A duplicate can only be considered as such if it matches all other duplicates in the group.
        This method registers that pair (A, B) represented in ``match`` as possible candidates and,
        if A and/or B end up matching every other duplicates in the group, add these duplicates to
        the group.

        :param tuple match: pair of :class:`~core.fs.File` to add
        """

        def add_candidate(item, match):
            matches = self.candidates[item]
            matches.add(match)
            if self.unordered <= matches:
                self.ordered.append(item)
                self.unordered.add(item)

        if match in self.matches:
            return
        self.matches.add(match)
        first, second, _ = match
        if first not in self.unordered:
            add_candidate(first, second)
        if second not in self.unordered:
            add_candidate(second, first)
        self._percentage = None
        self._matches_for_ref = None

    def discard_matches(self):
        """Remove all recorded matches that didn't result in a duplicate being added to the group.

        You can call this after the duplicate scanning process to free a bit of memory.
        """
        discarded = set(m for m in self.matches if not all(obj in self.unordered for obj in [m.first, m.second]))
        self.matches -= discarded
        self.candidates = defaultdict(set)
        return discarded

    def get_match_of(self, item):
        """Returns the match pair between ``item`` and :attr:`ref`."""
        if item is self.ref:
            return
        for m in self._get_matches_for_ref():
            if item in m:
                return m

    def prioritize(self, key_func, tie_breaker=None):
        """Reorders :attr:`ordered` according to ``key_func``.

        :param key_func: Key (f(x)) to be used for sorting
        :param tie_breaker: function to be used to select the reference position in case the top
                            duplicates have the same key_func() result.
        """
        # tie_breaker(ref, dupe) --> True if dupe should be ref
        # Returns True if anything changed during prioritization.
        new_order = sorted(self.ordered, key=lambda x: (-x.is_ref, key_func(x)))
        changed = new_order != self.ordered
        self.ordered = new_order
        if tie_breaker is None:
            return changed
        ref = self.ref
        key_value = key_func(ref)
        for dupe in self.dupes:
            if key_func(dupe) != key_value:
                break
            if tie_breaker(ref, dupe):
                ref = dupe
        if ref is not self.ref:
            self.switch_ref(ref)
            return True
        return changed

    def remove_dupe(self, item, discard_matches=True):
        try:
            self.ordered.remove(item)
            self.unordered.remove(item)
            self._percentage = None
            self._matches_for_ref = None
            if (len(self) > 1) and any(not getattr(item, "is_ref", False) for item in self):
                if discard_matches:
                    self.matches = set(m for m in self.matches if item not in m)
            else:
                self._clear()
        except ValueError:
            pass

    def switch_ref(self, with_dupe):
        """Make the :attr:`ref` dupe of the group switch position with ``with_dupe``."""
        if self.ref.is_ref:
            return False
        try:
            self.ordered.remove(with_dupe)
            self.ordered.insert(0, with_dupe)
            self._percentage = None
            self._matches_for_ref = None
            return True
        except ValueError:
            return False

    dupes = property(lambda self: self[1:])

    @property
    def percentage(self):
        if self._percentage is None:
            if self.dupes:
                matches = self._get_matches_for_ref()
                self._percentage = sum(match.percentage for match in matches) // len(matches)
            else:
                self._percentage = 0
        return self._percentage

    @property
    def ref(self):
        if self:
            return self[0]


def get_groups(matches):
    """Returns a list of :class:`Group` from ``matches``.

    Create groups out of match pairs in the smartest way possible.
    """
    matches.sort(key=lambda match: -match.percentage)
    dupe2group = {}
    groups = []
    try:
        for match in matches:
            first, second, _ = match
            first_group = dupe2group.get(first)
            second_group = dupe2group.get(second)
            if first_group:
                if second_group:
                    if first_group is second_group:
                        target_group = first_group
                    else:
                        continue
                else:
                    target_group = first_group
                    dupe2group[second] = target_group
            else:
                if second_group:
                    target_group = second_group
                    dupe2group[first] = target_group
                else:
                    target_group = Group()
                    groups.append(target_group)
                    dupe2group[first] = target_group
                    dupe2group[second] = target_group
            target_group.add_match(match)
    except MemoryError:
        del dupe2group
        del matches
        # should free enough memory to continue
        logging.warning("Memory Overflow. Groups: {0}".format(len(groups)))
    # Now that we have a group, we have to discard groups' matches and see if there're any "orphan"
    # matches, that is, matches that were candidate in a group but that none of their 2 files were
    # accepted in the group. With these orphan groups, it's safe to build additional groups
    matched_files = set(flatten(groups))
    orphan_matches = []
    for group in groups:
        orphan_matches += {
            m for m in group.discard_matches() if not any(obj in matched_files for obj in [m.first, m.second])
        }
    if groups and orphan_matches:
        groups += get_groups(orphan_matches)  # no job, as it isn't supposed to take a long time
    return groups
