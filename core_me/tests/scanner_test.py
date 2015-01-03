# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-10-23
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hscommon.path import Path

from core.engine import getwords
from core.tests.scanner_test import NamedObject, no
from ..scanner import *

def pytest_funcarg__fake_fileexists(request):
    # This is a hack to avoid invalidating all previous tests since the scanner started to test
    # for file existence before doing the match grouping.
    monkeypatch = request.getfuncargvalue('monkeypatch')
    monkeypatch.setattr(Path, 'exists', lambda _: True)

def test_priorize_me(fake_fileexists):
    # in ScannerME, bitrate goes first (right after is_ref) in priorization
    s = ScannerME()
    o1, o2 = no('foo', path='p1'), no('foo', path='p2')
    o1.bitrate = 1
    o2.bitrate = 2
    [group] = s.get_dupe_groups([o1, o2])
    assert group.ref is o2

