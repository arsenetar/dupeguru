# cxfreeze has some problems detecting all dependencies.
# This modules explicitly import those problematic modules.

import xml.etree.ElementPath
import gzip

import os

os.environ['QT_PLUGIN_PATH'] = 'qt4_plugins'