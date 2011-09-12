# Created By: Virgil Dupras
# Created On: 2011/09/07
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hscommon.util import dedupe, flatten,  rem_file_ext
from hscommon.trans import tr

class CriterionCategory:
    NAME = "Undefined"
    
    def __init__(self, results):
        self.results = results
    
    #--- Virtual
    def extract_value(self, dupe):
        raise NotImplementedError()
    
    def format_criterion_value(self, value):
        return value
    
    #--- Public
    def sort_key(self, dupe, crit_value):
        # Use this sort key when the order in the list depends on whether or not the dupe meets the
        # criteria. If it does, we return 0 (top of the list), if it doesn't, we return 1.
        if self.extract_value(dupe) == crit_value:
            return 0
        else:
            return 1
    
    def criteria_list(self):
        dupes = flatten(g[:] for g in self.results.groups)
        values = dedupe(self.extract_value(d) for d in dupes)
        return [Criterion(self, value) for value in values]

class Criterion:
    def __init__(self, category, value):
        self.category = category
        self.value = value
        self.display_value = category.format_criterion_value(value)
    
    def sort_key(self, dupe):
        return self.category.sort_key(dupe, self.value)
    
    @property
    def display(self):
        return "{} ({})".format(self.category.NAME, self.display_value)
    

class KindCategory(CriterionCategory):
    NAME = tr("Kind")
    
    def extract_value(self, dupe):
        return dupe.extension

class FolderCategory(CriterionCategory):
    NAME = tr("Folder")
    
    def extract_value(self, dupe):
        return dupe.folder_path
    
    def format_criterion_value(self, value):
        return str(value)

class FilenameCategory(CriterionCategory):
    NAME = tr("Filename")
    ENDS_WITH_NUMBER = 0
    DOESNT_END_WITH_NUMBER = 1
    
    def format_criterion_value(self, value):
        if value == self.ENDS_WITH_NUMBER:
            return tr("Ends with number")
        else:
            return tr("Doesn't end with number")
    
    def extract_value(self, dupe):
        return rem_file_ext(dupe.name)
    
    def sort_key(self, dupe, crit_value):
        value = self.extract_value(dupe)
        ends_with_digit = value.strip()[-1:].isdigit()
        if crit_value == self.ENDS_WITH_NUMBER:
            return 0 if ends_with_digit else 1
        else:
            return 1 if ends_with_digit else 0
    
    def criteria_list(self):
        return [Criterion(self, self.ENDS_WITH_NUMBER), Criterion(self, self.DOESNT_END_WITH_NUMBER)]

class NumericalCategory(CriterionCategory):
    HIGHEST = 0
    LOWEST = 1
    
    def format_criterion_value(self, value):
        return tr("Highest") if value == self.HIGHEST else tr("Lowest")
    
    def sort_key(self, dupe, crit_value):
        value = self.extract_value(dupe)
        if crit_value == self.HIGHEST: # we want highest values on top
            value *= -1
        return value
    
    def criteria_list(self):
        return [Criterion(self, self.HIGHEST), Criterion(self, self.LOWEST)]
    
class SizeCategory(NumericalCategory):
    NAME = tr("Size")
    
    def extract_value(self, dupe):
        return dupe.size

class MtimeCategory(NumericalCategory):
    NAME = tr("Modification Date")
    
    def extract_value(self, dupe):
        return dupe.mtime
    
    def format_criterion_value(self, value):
        return tr("Newest") if value == self.HIGHEST else tr("Oldest")

def all_categories():
    return [KindCategory, FolderCategory, FilenameCategory, SizeCategory, MtimeCategory]
