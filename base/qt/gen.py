#!/usr/bin/env python
# Unit Name: gen
# Created By: Virgil Dupras
# Created On: 2009-05-22
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

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