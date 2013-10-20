# Created By: Virgil Dupras
# Created On: 2013-10-12
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

class SpecialFolder:
    AppData = 1
    Cache = 2

def open_url(url):
    """Open ``url`` with the default browser.
    """
    _open_url(url)

def open_path(path):
    """Open ``path`` with its associated application.
    """
    _open_path(str(path))

def reveal_path(path):
    """Open the folder containing ``path`` with the default file browser.
    """
    _reveal_path(str(path))

def special_folder_path(special_folder):
    """Returns the path of ``special_folder``.
    
    ``special_folder`` is a SpecialFolder.* const.
    """
    return _special_folder_path(special_folder)

try:
    from cocoa import proxy
    _open_url = proxy.openURL_
    _open_path = proxy.openPath_
    _reveal_path = proxy.revealPath_
    
    def _special_folder_path(special_folder):
        if special_folder == SpecialFolder.Cache:
            return proxy.getCachePath()
        else:
            return proxy.getAppdataPath()
    
except ImportError:
    try:
        from PyQt5.QtCore import QUrl, QStandardPaths
        from PyQt5.QtGui import QDesktopServices
        import os.path as op
        def _open_path(path):
            url = QUrl.fromLocalFile(str(path))
            QDesktopServices.openUrl(url)
        
        def _reveal_path(path):
            _open_path(op.dirname(str(path)))
        
        def _special_folder_path(special_folder):
            if special_folder == SpecialFolder.Cache:
                qtfolder = QStandardPaths.CacheLocation
            else:
                qtfolder = QStandardPaths.DataLocation
            return QStandardPaths.standardLocations(qtfolder)[0]
        
    except ImportError:
        raise Exception("Can't setup desktop functions!")
