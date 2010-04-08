# cxfreeze has some problems detecting all dependencies.
# This modules explicitly import those problematic modules.

import lxml._elementpath
import gzip

import os

os.environ['QT_PLUGIN_PATH'] = 'qt4_plugins'