# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-12-30
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import sys
from optparse import OptionParser

import yaml

def main(edition, ui, dev):
    if edition not in ('se', 'me', 'pe'):
        edition = 'se'
    if ui not in ('cocoa', 'qt'):
        ui = 'cocoa' if sys.platform == 'darwin' else 'qt'
    build_type = 'Dev' if dev else 'Release'
    print("Configuring dupeGuru {0} for UI {1} ({2})".format(edition.upper(), ui, build_type))
    conf = {
        'edition': edition,
        'ui': ui,
        'dev': dev,
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
    (options, args) = parser.parse_args()
    main(options.edition, options.ui, options.dev)
