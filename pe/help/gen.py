#!/usr/bin/env python
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from hsdocgen import generate_help, filters

def generate(windows=False):
    tix = filters.tixgen("https://hardcoded.lighthouseapp.com/projects/31699-dupeguru/tickets/{0}")
    generate_help.main('.', 'dupeguru_pe_help', force_render=True, tix=tix, windows=windows)
