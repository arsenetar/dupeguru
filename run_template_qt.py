#!/usr/bin/env python3

import sys
import os
import os.path as op
import runpy

def main():
    scriptpath = op.abspath(__file__)
    scriptfolder = op.dirname(scriptpath)
    sys.path.insert(0, scriptfolder)
    del sys.argv[0]
    runpy.run_module('qt.{edition}.start', run_name="__main__")

if __name__ == '__main__':
    sys.exit(main())