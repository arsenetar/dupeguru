# Created On: 2011/09/16
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from hscommon.trans import trget

from core.prioritize import (
    KindCategory,
    FolderCategory,
    FilenameCategory,
    NumericalCategory,
    SizeCategory,
    MtimeCategory,
)

coltr = trget("columns")


class DimensionsCategory(NumericalCategory):
    NAME = coltr("Dimensions")

    def extract_value(self, dupe):
        return dupe.dimensions

    def invert_numerical_value(self, value):
        width, height = value
        return (-width, -height)


def all_categories():
    return [
        KindCategory,
        FolderCategory,
        FilenameCategory,
        SizeCategory,
        DimensionsCategory,
        MtimeCategory,
    ]
