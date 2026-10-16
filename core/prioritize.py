# Created By: Virgil Dupras
# Created On: 2011/09/07
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

import re
from functools import total_ordering
from typing import Any, List, Union

from hscommon.util import dedupe, flatten, rem_file_ext
from hscommon.trans import trget, tr

coltr = trget("columns")


@total_ordering
class Descending:
    """Sort key wrapper that reverses the order of the key it wraps.

    Numbers can be negated to sort them in descending order, but strings and lists can't.
    """

    def __init__(self, key: Any) -> None:
        self.key = key

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Descending) and self.key == other.key

    def __lt__(self, other: "Descending") -> bool:
        return self.key > other.key


def natural_sort_key(text: str) -> List[Union[str, int]]:
    """Sort key that compares runs of digits by their value, so that "file9" comes before "file10".

    Everything else compares case-insensitively.
    """
    # With a capturing group, re.split() alternates text and digit runs: the digit runs are always
    # at the odd indexes, so two keys never compare a number with a string. \d only matches the
    # decimal digits int() accepts, unlike str.isdigit(), which also accepts "²".
    parts = re.split(r"(\d+)", text.casefold())
    return [int(part) if i % 2 else part for i, part in enumerate(parts)]


class CriterionCategory:
    NAME = "Undefined"

    def __init__(self, results):
        self.results = results

    # --- Virtual
    def extract_value(self, dupe):
        raise NotImplementedError()

    def format_criterion_value(self, value):
        return value

    def sort_key(self, dupe, crit_value):
        raise NotImplementedError()

    def criteria_list(self):
        raise NotImplementedError()


class Criterion:
    def __init__(self, category, value):
        self.category = category
        self.value = value
        self.display_value = category.format_criterion_value(value)

    def sort_key(self, dupe):
        return self.category.sort_key(dupe, self.value)

    @property
    def display(self):
        return f"{self.category.NAME} ({self.display_value})"


class ValueListCategory(CriterionCategory):
    def sort_key(self, dupe, crit_value):
        # Use this sort key when the order in the list depends on whether or not the dupe meets the
        # criteria. If it does, we return 0 (top of the list), if it doesn't, we return 1.
        if self.extract_value(dupe) == crit_value:
            return 0
        else:
            return 1

    def criteria_list(self):
        dupes = flatten(g[:] for g in self.results.groups)
        values = sorted(dedupe(self.extract_value(d) for d in dupes))
        return [Criterion(self, value) for value in values]


class KindCategory(ValueListCategory):
    NAME = coltr("Kind")

    def extract_value(self, dupe):
        value = dupe.extension
        if not value:
            value = tr("None")
        return value


class FolderCategory(ValueListCategory):
    NAME = coltr("Folder")

    def extract_value(self, dupe):
        return dupe.folder_path

    def format_criterion_value(self, value):
        return str(value)

    def sort_key(self, dupe, crit_value):
        value = self.extract_value(dupe)
        # This is instead of using is_relative_to() which was added in py 3.9
        try:
            value.relative_to(crit_value)
        except ValueError:
            return 1
        return 0


class FilenameCategory(CriterionCategory):
    NAME = coltr("Filename")
    ENDS_WITH_NUMBER = 0
    DOESNT_END_WITH_NUMBER = 1
    LONGEST = 2
    SHORTEST = 3
    LONGEST_PATH = 4
    SHORTEST_PATH = 5
    A_TO_Z = 6
    Z_TO_A = 7
    NATURAL_A_TO_Z = 8
    NATURAL_Z_TO_A = 9

    def format_criterion_value(self, value):
        return {
            self.ENDS_WITH_NUMBER: tr("Ends with number"),
            self.DOESNT_END_WITH_NUMBER: tr("Doesn't end with number"),
            self.LONGEST: tr("Longest"),
            self.SHORTEST: tr("Shortest"),
            self.LONGEST_PATH: tr("Longest Path"),
            self.SHORTEST_PATH: tr("Shortest Path"),
            self.A_TO_Z: tr("A to Z"),
            self.Z_TO_A: tr("Z to A"),
            self.NATURAL_A_TO_Z: tr("A to Z, natural order"),
            self.NATURAL_Z_TO_A: tr("Z to A, natural order"),
        }[value]

    def extract_value(self, dupe):
        return rem_file_ext(dupe.name)

    def sort_key(self, dupe, crit_value):
        value = self.extract_value(dupe)
        if crit_value in {self.ENDS_WITH_NUMBER, self.DOESNT_END_WITH_NUMBER}:
            ends_with_digit = value.strip()[-1:].isdigit()
            if crit_value == self.ENDS_WITH_NUMBER:
                return 0 if ends_with_digit else 1
            else:
                return 1 if ends_with_digit else 0
        elif crit_value == self.LONGEST_PATH:
            return len(str(dupe.folder_path)) * -1
        elif crit_value == self.SHORTEST_PATH:
            return len(str(dupe.folder_path))
        elif crit_value in {self.A_TO_Z, self.Z_TO_A}:
            key = value.casefold()
            return key if crit_value == self.A_TO_Z else Descending(key)
        elif crit_value in {self.NATURAL_A_TO_Z, self.NATURAL_Z_TO_A}:
            key = natural_sort_key(value)
            return key if crit_value == self.NATURAL_A_TO_Z else Descending(key)
        else:
            value = len(value)
            if crit_value == self.LONGEST:
                value *= -1  # We want the biggest values on top
            return value

    def criteria_list(self):
        return [
            Criterion(self, crit_value)
            for crit_value in [
                self.ENDS_WITH_NUMBER,
                self.DOESNT_END_WITH_NUMBER,
                self.LONGEST,
                self.SHORTEST,
                self.LONGEST_PATH,
                self.SHORTEST_PATH,
                self.A_TO_Z,
                self.Z_TO_A,
                self.NATURAL_A_TO_Z,
                self.NATURAL_Z_TO_A,
            ]
        ]


class NumericalCategory(CriterionCategory):
    HIGHEST = 0
    LOWEST = 1

    def format_criterion_value(self, value):
        return tr("Highest") if value == self.HIGHEST else tr("Lowest")

    def invert_numerical_value(self, value):  # Virtual
        return value * -1

    def sort_key(self, dupe, crit_value):
        value = self.extract_value(dupe)
        if crit_value == self.HIGHEST:  # we want highest values on top
            value = self.invert_numerical_value(value)
        return value

    def criteria_list(self):
        return [Criterion(self, self.HIGHEST), Criterion(self, self.LOWEST)]


class SizeCategory(NumericalCategory):
    NAME = coltr("Size")

    def extract_value(self, dupe):
        return dupe.size


class MtimeCategory(NumericalCategory):
    NAME = coltr("Modification")

    def extract_value(self, dupe):
        return dupe.mtime

    def format_criterion_value(self, value):
        return tr("Newest") if value == self.HIGHEST else tr("Oldest")


def all_categories():
    return [KindCategory, FolderCategory, FilenameCategory, SizeCategory, MtimeCategory]
