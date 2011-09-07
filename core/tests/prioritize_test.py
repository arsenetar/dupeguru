# Created By: Virgil Dupras
# Created On: 2011/09/07
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from itertools import combinations

from .base import TestApp, NamedObject, with_app, eq_
from ..engine import Group, Match

no = NamedObject

def app_with_dupes(dupes):
    # Creates an app with specified dupes. dupes is a list of lists, each list in the list being
    # a dupe group. We cheat a little bit by creating dupe groups manually instead of running a
    # dupe scan, but it simplifies the test code quite a bit
    app = TestApp()
    groups = []
    for dupelist in dupes:
        g = Group()
        for dupe1, dupe2 in combinations(dupelist, 2):
            g.add_match(Match(dupe1, dupe2, 100))
        groups.append(g)
    app.app.results.groups = groups
    app.app._results_changed()
    return app

#---
def app_normal_results():
    # Just some results, with different extensions and size, for good measure.
    dupes = [
        [no('foo1.ext1', size=1), no('foo2.ext2', size=2)],
    ]
    return app_with_dupes(dupes)

@with_app(app_normal_results)
def test_kind_subcrit(app):
    # The subcriteria of the "Kind" criteria is a list of extensions contained in the dupes.
    app.select_pri_criterion("Kind")
    eq_(app.pdialog.criteria_list, ['ext1', 'ext2'])