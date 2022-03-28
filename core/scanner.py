# Copyright 2016 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

import logging
import re
import os.path as op
from collections import namedtuple

from hscommon.jobprogress import job
from hscommon.util import dedupe, rem_file_ext, get_file_ext
from hscommon.trans import tr

from . import engine

# It's quite ugly to have scan types from all editions all put in the same class, but because there's
# there will be some nasty bugs popping up (ScanType is used in core when in should exclusively be
# used in core_*). One day I'll clean this up.


class ScanType:
    FILENAME = 0
    FIELDS = 1
    FIELDSNOORDER = 2
    TAG = 3
    FOLDERS = 4
    CONTENTS = 5

    # PE
    FUZZYBLOCK = 10
    EXIFTIMESTAMP = 11


ScanOption = namedtuple("ScanOption", "scan_type label")

SCANNABLE_TAGS = ["track", "artist", "album", "title", "genre", "year"]

RE_DIGIT_ENDING = re.compile(r"\d+|\(\d+\)|\[\d+\]|{\d+}")


def is_same_with_digit(name, refname):
    # Returns True if name is the same as refname, but with digits (with brackets or not) at the end
    if not name.startswith(refname):
        return False
    end = name[len(refname) :].strip()
    return RE_DIGIT_ENDING.match(end) is not None


def remove_dupe_paths(files):
    # Returns files with duplicates-by-path removed. Files with the exact same path are considered
    # duplicates and only the first file to have a path is kept. In certain cases, we have files
    # that have the same path, but not with the same case, that's why we normalize. However, we also
    # have case-sensitive filesystems, and in those, we don't want to falsely remove duplicates,
    # that's why we have a `samefile` mechanism.
    result = []
    path2file = {}
    for f in files:
        normalized = str(f.path).lower()
        if normalized in path2file:
            try:
                if op.samefile(normalized, str(path2file[normalized].path)):
                    continue  # same file, it's a dupe
                else:
                    pass  # We don't treat them as dupes
            except OSError:
                continue  # File doesn't exist? Well, treat them as dupes
        else:
            path2file[normalized] = f
        result.append(f)
    return result


class Scanner:
    def __init__(self):
        self.discarded_file_count = 0

    def _getmatches(self, files, j):
        if (
            self.size_threshold
            or self.large_size_threshold
            or self.scan_type
            in {
                ScanType.CONTENTS,
                ScanType.FOLDERS,
            }
        ):
            j = j.start_subjob([2, 8])
            for f in j.iter_with_progress(files, tr("Read size of %d/%d files")):
                f.size  # pre-read, makes a smoother progress if read here (especially for bundles)
            if self.size_threshold:
                files = [f for f in files if f.size >= self.size_threshold]
            if self.large_size_threshold:
                files = [f for f in files if f.size <= self.large_size_threshold]
        if self.scan_type in {ScanType.CONTENTS, ScanType.FOLDERS}:
            return engine.getmatches_by_contents(files, bigsize=self.big_file_size_threshold, j=j)
        else:
            j = j.start_subjob([2, 8])
            kw = {}
            kw["match_similar_words"] = self.match_similar_words
            kw["weight_words"] = self.word_weighting
            kw["min_match_percentage"] = self.min_match_percentage
            if self.scan_type == ScanType.FIELDSNOORDER:
                self.scan_type = ScanType.FIELDS
                kw["no_field_order"] = True
            func = {
                ScanType.FILENAME: lambda f: engine.getwords(rem_file_ext(f.name)),
                ScanType.FIELDS: lambda f: engine.getfields(rem_file_ext(f.name)),
                ScanType.TAG: lambda f: [
                    engine.getwords(str(getattr(f, attrname)))
                    for attrname in SCANNABLE_TAGS
                    if attrname in self.scanned_tags
                ],
            }[self.scan_type]
            for f in j.iter_with_progress(files, tr("Read metadata of %d/%d files")):
                logging.debug("Reading metadata of %s", f.path)
                f.words = func(f)
            return engine.getmatches(files, j=j, **kw)

    @staticmethod
    def _key_func(dupe):
        return -dupe.size

    @staticmethod
    def _tie_breaker(ref, dupe):
        refname = rem_file_ext(ref.name).lower()
        dupename = rem_file_ext(dupe.name).lower()
        if "copy" in dupename:
            return False
        if "copy" in refname:
            return True
        if is_same_with_digit(dupename, refname):
            return False
        if is_same_with_digit(refname, dupename):
            return True
        return len(dupe.path.parts) > len(ref.path.parts)

    @staticmethod
    def get_scan_options():
        """Returns a list of scanning options for this scanner.

        Returns a list of ``ScanOption``.
        """
        raise NotImplementedError()

    def get_dupe_groups(self, files, ignore_list=None, j=job.nulljob):
        for f in (f for f in files if not hasattr(f, "is_ref")):
            f.is_ref = False
        files = remove_dupe_paths(files)
        logging.info("Getting matches. Scan type: %d", self.scan_type)
        matches = self._getmatches(files, j)
        logging.info("Found %d matches" % len(matches))
        j.set_progress(100, tr("Almost done! Fiddling with results..."))
        # In removing what we call here "false matches", we first want to remove, if we scan by
        # folders, we want to remove folder matches for which the parent is also in a match (they're
        # "duplicated duplicates if you will). Then, we also don't want mixed file kinds if the
        # option isn't enabled, we want matches for which both files exist and, lastly, we don't
        # want matches with both files as ref.
        if self.scan_type == ScanType.FOLDERS and matches:
            allpath = {m.first.path for m in matches}
            allpath |= {m.second.path for m in matches}
            sortedpaths = sorted(allpath)
            toremove = set()
            last_parent_path = sortedpaths[0]
            for p in sortedpaths[1:]:
                if last_parent_path in p.parents:
                    toremove.add(p)
                else:
                    last_parent_path = p
            matches = [m for m in matches if m.first.path not in toremove or m.second.path not in toremove]
        if not self.mix_file_kind:
            matches = [m for m in matches if get_file_ext(m.first.name) == get_file_ext(m.second.name)]
        matches = [m for m in matches if m.first.path.exists() and m.second.path.exists()]
        matches = [m for m in matches if not (m.first.is_ref and m.second.is_ref)]
        if ignore_list:
            matches = [m for m in matches if not ignore_list.are_ignored(str(m.first.path), str(m.second.path))]
        logging.info("Grouping matches")
        groups = engine.get_groups(matches)
        if self.scan_type in {
            ScanType.FILENAME,
            ScanType.FIELDS,
            ScanType.FIELDSNOORDER,
            ScanType.TAG,
        }:
            matched_files = dedupe([m.first for m in matches] + [m.second for m in matches])
            self.discarded_file_count = len(matched_files) - sum(len(g) for g in groups)
        else:
            # Ticket #195
            # To speed up the scan, we don't bother comparing contents of files that are both ref
            # files. However, this messes up "discarded" counting because there's a missing match
            # in cases where we end up with a dupe group anyway (with a non-ref file). Because it's
            # impossible to have discarded matches in exact dupe scans, we simply set it at 0, thus
            # bypassing our tricky problem.
            # Also, although ScanType.FuzzyBlock is not always doing exact comparisons, we also
            # bypass ref comparison, thus messing up with our "discarded" count. So we're
            # effectively disabling the "discarded" feature in PE, but it's better than falsely
            # reporting discarded matches.
            self.discarded_file_count = 0
        groups = [g for g in groups if any(not f.is_ref for f in g)]
        logging.info("Created %d groups" % len(groups))
        for g in groups:
            g.prioritize(self._key_func, self._tie_breaker)
        return groups

    match_similar_words = False
    min_match_percentage = 80
    mix_file_kind = True
    scan_type = ScanType.FILENAME
    scanned_tags = {"artist", "title"}
    size_threshold = 0
    large_size_threshold = 0
    big_file_size_threshold = 0
    word_weighting = False
