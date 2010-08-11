# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-12-30
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import sys
import os
import os.path as op

import yaml

from hscommon.build import add_to_pythonpath

def main():
    conf = yaml.load(open('conf.yaml'))
    edition = conf['edition']
    ui = conf['ui']
    dev = conf['dev']
    print("Running dupeGuru {0} with UI {1}".format(edition.upper(), ui))
    if ui == 'cocoa':
        subfolder = 'dev' if dev else 'release'
        app_path = {
            'se': 'cocoa/se/build/{0}/dupeGuru.app',
            'me': 'cocoa/me/build/{0}/dupeGuru\\ ME.app',
            'pe': 'cocoa/pe/build/{0}/dupeGuru\\ PE.app',
        }[edition].format(subfolder)
        os.system('open {0}'.format(app_path))
    elif ui == 'qt':
        add_to_pythonpath('.')
        add_to_pythonpath('qt')
        add_to_pythonpath(op.join('qt', 'base'))
        os.chdir(op.join('qt', edition))
        os.system('python3 start.py')
        os.chdir('..')

if __name__ == '__main__':
    main()