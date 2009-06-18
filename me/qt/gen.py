#!/usr/bin/env python
# Unit Name: gen
# Created By: Virgil Dupras
# Created On: 2009-05-22
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

import os

from hsutil.build import print_and_do

os.chdir('base')
print_and_do('python gen.py')
os.chdir('..')

print_and_do("pyuic4 details_dialog.ui > details_dialog_ui.py")
print_and_do("pyuic4 preferences_dialog.ui > preferences_dialog_ui.py")

os.chdir('help')
print_and_do('python gen.py')
os.chdir('..')
