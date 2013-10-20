# Created By: Virgil Dupras
# Created On: 2011-02-01
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import sys
import io
import os.path as op
import os
import logging

from hscommon.util import first

from PyQt5.QtCore import QStandardPaths
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QDesktopWidget, QSpacerItem, QSizePolicy, QAction, QHBoxLayout

def moveToScreenCenter(widget):
    frame = widget.frameGeometry()
    frame.moveCenter(QDesktopWidget().availableGeometry().center())
    widget.move(frame.topLeft())

def verticalSpacer(size=None):
    if size:
        return QSpacerItem(1, size, QSizePolicy.Fixed, QSizePolicy.Fixed)
    else:
        return QSpacerItem(1, 1, QSizePolicy.Fixed, QSizePolicy.MinimumExpanding)

def horizontalSpacer(size=None):
    if size:
        return QSpacerItem(size, 1, QSizePolicy.Fixed, QSizePolicy.Fixed)
    else:
        return QSpacerItem(1, 1, QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)

def horizontalWrap(widgets):
    """Wrap all widgets in `widgets` in a horizontal layout.
    
    If, instead of placing a widget in your list, you place an int or None, an horizontal spacer
    with the width corresponding to the int will be placed (0 or None means an expanding spacer).
    """
    layout = QHBoxLayout()
    for widget in widgets:
        if widget is None or isinstance(widget, int):
            layout.addItem(horizontalSpacer(size=widget))
        else:
            layout.addWidget(widget)
    return layout

def createActions(actions, target):
    # actions = [(name, shortcut, icon, desc, func)]
    for name, shortcut, icon, desc, func in actions:
        action = QAction(target)
        if icon:
            action.setIcon(QIcon(QPixmap(':/' + icon)))
        if shortcut:
            action.setShortcut(shortcut)
        action.setText(desc)
        action.triggered.connect(func)
        setattr(target, name, action)

def setAccelKeys(menu):
    actions = menu.actions()
    titles = [a.text() for a in actions]
    available_characters = {c.lower() for s in titles for c in s if c.isalpha()}
    for action in actions:
        text = action.text()
        c = first(c for c in text if c.lower() in available_characters)
        if c is None:
            continue
        i = text.index(c)
        newtext = text[:i] + '&' + text[i:]
        available_characters.remove(c.lower())
        action.setText(newtext)

def getAppData():
    return QStandardPaths.standardLocations(QStandardPaths.DataLocation)[0]

class SysWrapper(io.IOBase):
    def write(self, s):
        if s.strip(): # don't log empty stuff
            logging.warning(s)

def setupQtLogging(level=logging.WARNING):
    # Under Qt, we log in "debug.log" in appdata. Moreover, when under cx_freeze, we have a
    # problem because sys.stdout and sys.stderr are None, so we need to replace them with a
    # wrapper that logs with the logging module.
    appdata = getAppData()
    if not op.exists(appdata):
        os.makedirs(appdata)
    # For basicConfig() to work, we have to be sure that no logging has taken place before this call.
    logging.basicConfig(filename=op.join(appdata, 'debug.log'), level=level,
        format='%(asctime)s - %(levelname)s - %(message)s')
    if sys.stderr is None: # happens under a cx_freeze environment
        sys.stderr = SysWrapper()
    if sys.stdout is None:
        sys.stdout = SysWrapper()

def escapeamp(s):
    # Returns `s` with escaped ampersand (& --> &&). QAction text needs to have & escaped because
    # that character is used to define "accel keys".
    return s.replace('&', '&&')
