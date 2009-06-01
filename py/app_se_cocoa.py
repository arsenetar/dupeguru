#!/usr/bin/env python
# Unit Name: app_se_cocoa
# Created By: Virgil Dupras
# Created On: 2009-05-24
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

import app_cocoa, data

class DupeGuru(app_cocoa.DupeGuru):
    def __init__(self):
        app_cocoa.DupeGuru.__init__(self, data, 'dupeguru', appid=4)
    
