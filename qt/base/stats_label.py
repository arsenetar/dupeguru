# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-02-12
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from core.gui.stats_label import StatsLabel as StatsLabelModel

class StatsLabel(object):
    def __init__(self, app, view):
        self.view = view
        self.model = StatsLabelModel(self, app)
        self.model.connect()
    
    def refresh(self):
        self.view.setText(self.model.display)
    
