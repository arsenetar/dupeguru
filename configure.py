# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-12-30
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import sys
from optparse import OptionParser

import yaml

def main(edition, ui, dev, build64):
    if edition not in ('se', 'me', 'pe'):
        edition = 'se'
    if ui not in ('cocoa', 'qt'):
        ui = 'cocoa' if sys.platform == 'darwin' else 'qt'
    build_type = 'Dev' if dev else 'Release'
    print "Configuring dupeGuru {0} for UI {1} ({2})".format(edition.upper(), ui, build_type)
    if build64:
        print "If possible, 64-bit builds will be made"
    conf = {
        'edition': edition,
        'ui': ui,
        'dev': dev,
        'build64': build64,
    }
    yaml.dump(conf, open('conf.yaml', 'w'))

if __name__ == '__main__':
    usage = "usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option('--edition', dest='edition',
        help="dupeGuru edition to build (se, me or pe). Default is se.")
    parser.add_option('--ui', dest='ui',
        help="Type of UI to build. 'qt' or 'cocoa'. Default is determined by your system.")
    parser.add_option('--dev', action='store_true', dest='dev', default=False,
        help="If this flag is set, will configure for dev builds.")
    parser.add_option('--64bit', action='store_true', dest='build64', default=False,
        help="Build 64-bit app if possible.")
    (options, args) = parser.parse_args()
    main(options.edition, options.ui, options.dev, options.build64)
