#!/usr/bin/env python
# Created By: Virgil Dupras
# Created On: 2009-05-22
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import os

def print_and_do(cmd):
    print cmd
    os.system(cmd)

print_and_do("pyuic4 main_window.ui > main_window_ui.py")
print_and_do("pyuic4 directories_dialog.ui > directories_dialog_ui.py")
print_and_do("pyuic4 about_box.ui > about_box_ui.py")
print_and_do("pyuic4 reg_submit_dialog.ui > reg_submit_dialog_ui.py")
print_and_do("pyuic4 reg_demo_dialog.ui > reg_demo_dialog_ui.py")
print_and_do("pyuic4 error_report_dialog.ui > error_report_dialog_ui.py")
print_and_do("pyrcc4 dg.qrc > dg_rc.py")