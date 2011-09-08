# Created By: Virgil Dupras
# Created On: 2011/09/07
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hscommon.util import dedupe, flatten

class CriterionCategory:
    NAME = "Undefined"
    
    def __init__(self, results):
        self.results = results
    
    #--- Virtual
    def _extract_value(self, dupe):
        raise NotImplementedError()
    
    #--- Public
    def criteria_list(self):
        dupes = flatten(g[:] for g in self.results.groups)
        values = dedupe(self._extract_value(d) for d in dupes)
        return [Criterion(self, value) for value in values]

class Criterion:
    def __init__(self, category, value):
        self.category = category
        self.value = value
    
    def test_dupe(self, dupe):
        return self.category._extract_value(dupe) == self.value
    
    @property
    def display(self):
        return "{} ({})".format(self.category, self.value)
    

class KindCategory(CriterionCategory):
    NAME = "Kind"
    
    def _extract_value(self, dupe):
        return dupe.extension
