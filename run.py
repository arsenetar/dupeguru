# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-12-30
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import sys
import os
import os.path as op

import yaml

from hsutil.build import add_to_pythonpath

def main():
    conf = yaml.load(open('conf.yaml'))
    edition = conf['edition']
    ui = conf['ui']
    print "Running dupeGuru {0} with UI {1}".format(edition.upper(), ui)
    if ui == 'cocoa':
        app_path = {
            'se': 'cocoa/se/build/Release/dupeGuru.app',
            'me': 'cocoa/me/build/Release/dupeGuru\\ ME.app',
            'pe': 'cocoa/pe/build/Release/dupeGuru\\ PE.app',
        }[edition]
        os.system('open {0}'.format(app_path))
    elif ui == 'qt':
        add_to_pythonpath('.')
        add_to_pythonpath('qt')
        os.chdir(op.join('qt', edition))
        os.system('python start.py')
        os.chdir('..')

if __name__ == '__main__':
    main()