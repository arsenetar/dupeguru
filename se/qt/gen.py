#!/usr/bin/env python
# Created By: Virgil Dupras
# Created On: 2009-05-24
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

os.chdir('base')
print_and_do('python gen.py')
os.chdir('..')

print_and_do("pyuic4 details_dialog.ui > details_dialog_ui.py")
print_and_do("pyuic4 preferences_dialog.ui > preferences_dialog_ui.py")

os.chdir('help')
print_and_do('python gen.py')
os.chdir('..')
