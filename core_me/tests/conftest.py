# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-07-11
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

# This unit is required to make tests work with py.test. When running

import py

def get_testunit(item):
    if hasattr(item, 'obj'):
        testunit = py.builtin._getimself(item.obj)
        if hasattr(testunit, 'global_setup'):
            return testunit

def pytest_runtest_setup(item):
    testunit = get_testunit(item)
    if testunit is not None:
        testunit.global_setup()

def pytest_runtest_teardown(item):
    testunit = get_testunit(item)
    if testunit is not None:
        testunit.global_teardown()
