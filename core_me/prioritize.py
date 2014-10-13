# Created On: 2011/09/16
# Copyright 2014 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "BSD" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.hardcoded.net/licenses/bsd_license

from hscommon.trans import trget

from core.prioritize import (
    KindCategory, FolderCategory, FilenameCategory, NumericalCategory,
    SizeCategory, MtimeCategory
)

coltr = trget('columns')

class DurationCategory(NumericalCategory):
    NAME = coltr("Duration")

    def extract_value(self, dupe):
        return dupe.duration

class BitrateCategory(NumericalCategory):
    NAME = coltr("Bitrate")

    def extract_value(self, dupe):
        return dupe.bitrate

class SamplerateCategory(NumericalCategory):
    NAME = coltr("Samplerate")

    def extract_value(self, dupe):
        return dupe.samplerate

def all_categories():
    return [
        KindCategory, FolderCategory, FilenameCategory, SizeCategory, DurationCategory,
        BitrateCategory, SamplerateCategory, MtimeCategory
    ]

