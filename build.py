# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-12-30
# $Id$
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import sys
import os
import os.path as op

import yaml

from hsutil.build import move_testdata_out, put_testdata_back, add_to_pythonpath

def main():
    conf = yaml.load(open('conf.yaml'))
    edition = conf['edition']
    ui = conf['ui']
    dev = conf['dev']
    print "Building dupeGuru {0} with UI {1}".format(edition.upper(), ui)
    add_to_pythonpath('.')
    if dev:
        print "Building in Dev mode"
    print "Generating Help"
    windows = sys.platform=='win32'
    if edition == 'se':
        import help_se.gen
        help_se.gen.generate(windows=windows, force_render=not dev)
    elif edition == 'me':
        import help_me.gen
        help_me.gen.generate(windows=windows, force_render=not dev)
    elif edition == 'pe':
        import help_pe.gen
        help_pe.gen.generate(windows=windows, force_render=not dev)
    
    print "Building dupeGuru"
    if edition == 'pe':
        os.chdir('core_pe')
        os.system('python gen.py')
        os.chdir('..')
    if ui == 'cocoa':
        move_log = move_testdata_out()
        try:
            os.chdir(op.join('cocoa', edition))
            if dev:
                os.system('python gen.py --dev')
            else:
                os.system('python gen.py')
            os.chdir(op.join('..', '..'))
        finally:
            put_testdata_back(move_log)
    elif ui == 'qt':
        os.chdir(op.join('qt', edition))
        os.system('python gen.py')
        os.chdir(op.join('..', '..'))

if __name__ == '__main__':
    main()
