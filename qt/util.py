# Created By: Virgil Dupras
# Created On: 2011-02-01
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

import sys
import io
import os.path as op
import os
import logging

from core.util import executable_folder
from hscommon.util import first
from hscommon.plat import ISWINDOWS

from PyQt5.QtCore import QStandardPaths, QSettings
from PyQt5.QtGui import QPixmap, QIcon, QGuiApplication
from PyQt5.QtWidgets import (
    QSpacerItem,
    QSizePolicy,
    QAction,
    QHBoxLayout,
)


def move_to_screen_center(widget):
    frame = widget.frameGeometry()
    if QGuiApplication.screenAt(frame.center()) is None:
        # if center not on any screen use default screen
        screen = QGuiApplication.screens()[0].availableGeometry()
    else:
        screen = QGuiApplication.screenAt(frame.center()).availableGeometry()
    # moves to center of screen if partially off screen
    if screen.contains(frame) is False:
        # make sure the frame is not larger than screen
        # resize does not seem to take frame size into account (move does)
        widget.resize(frame.size().boundedTo(screen.size() - (frame.size() - widget.size())))
        frame = widget.frameGeometry()
        frame.moveCenter(screen.center())
        widget.move(frame.topLeft())


def vertical_spacer(size=None):
    if size:
        return QSpacerItem(1, size, QSizePolicy.Fixed, QSizePolicy.Fixed)
    else:
        return QSpacerItem(1, 1, QSizePolicy.Fixed, QSizePolicy.MinimumExpanding)


def horizontal_spacer(size=None):
    if size:
        return QSpacerItem(size, 1, QSizePolicy.Fixed, QSizePolicy.Fixed)
    else:
        return QSpacerItem(1, 1, QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)


def horizontal_wrap(widgets):
    """Wrap all widgets in `widgets` in a horizontal layout.

    If, instead of placing a widget in your list, you place an int or None, an horizontal spacer
    with the width corresponding to the int will be placed (0 or None means an expanding spacer).
    """
    layout = QHBoxLayout()
    for widget in widgets:
        if widget is None or isinstance(widget, int):
            layout.addItem(horizontal_spacer(size=widget))
        else:
            layout.addWidget(widget)
    return layout


def create_actions(actions, target):
    # actions are list of (name, shortcut, icon, desc, func)
    for name, shortcut, icon, desc, func in actions:
        action = QAction(target)
        if icon:
            action.setIcon(QIcon(QPixmap(":/" + icon)))
        if shortcut:
            action.setShortcut(shortcut)
        action.setText(desc)
        action.triggered.connect(func)
        setattr(target, name, action)


def set_accel_keys(menu):
    actions = menu.actions()
    titles = [a.text() for a in actions]
    available_characters = {c.lower() for s in titles for c in s if c.isalpha()}
    for action in actions:
        text = action.text()
        c = first(c for c in text if c.lower() in available_characters)
        if c is None:
            continue
        i = text.index(c)
        newtext = text[:i] + "&" + text[i:]
        available_characters.remove(c.lower())
        action.setText(newtext)


def get_appdata(portable=False):
    if portable:
        return op.join(executable_folder(), "data")
    else:
        return QStandardPaths.standardLocations(QStandardPaths.AppDataLocation)[0]


class SysWrapper(io.IOBase):
    def write(self, s):
        if s.strip():  # don't log empty stuff
            logging.warning(s)


def setup_qt_logging(level=logging.WARNING, log_to_stdout=False):
    # Under Qt, we log in "debug.log" in appdata. Moreover, when under cx_freeze, we have a
    # problem because sys.stdout and sys.stderr are None, so we need to replace them with a
    # wrapper that logs with the logging module.
    appdata = get_appdata()
    if not op.exists(appdata):
        os.makedirs(appdata)
    # Setup logging
    # Have to use full configuration over basicConfig as FileHandler encoding was not being set.
    filename = op.join(appdata, "debug.log") if not log_to_stdout else None
    log = logging.getLogger()
    handler = logging.FileHandler(filename, "a", "utf-8")
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    log.addHandler(handler)
    if sys.stderr is None:  # happens under a cx_freeze environment
        sys.stderr = SysWrapper()
    if sys.stdout is None:
        sys.stdout = SysWrapper()


def escape_amp(s):
    # Returns `s` with escaped ampersand (& --> &&). QAction text needs to have & escaped because
    # that character is used to define "accel keys".
    return s.replace("&", "&&")


def create_qsettings():
    # Create a QSettings instance with the correct arguments.
    config_location = op.join(executable_folder(), "settings.ini")
    if op.isfile(config_location):
        settings = QSettings(config_location, QSettings.IniFormat)
        settings.setValue("Portable", True)
    elif ISWINDOWS:
        # On windows use an ini file in the AppDataLocation instead of registry if possible as it
        # makes it easier for a user to clear it out when there are issues.
        locations = QStandardPaths.standardLocations(QStandardPaths.AppDataLocation)
        if locations:
            settings = QSettings(op.join(locations[0], "settings.ini"), QSettings.IniFormat)
        else:
            settings = QSettings()
        settings.setValue("Portable", False)
    else:
        settings = QSettings()
        settings.setValue("Portable", False)
    return settings
