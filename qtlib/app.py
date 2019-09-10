# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-10-16
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from PyQt5.QtCore import pyqtSignal, QTimer, QObject

class Application(QObject):
    finishedLaunching = pyqtSignal()

    def __init__(self):
        QObject.__init__(self)
        QTimer.singleShot(0, self.__launchTimerTimedOut)

    def __launchTimerTimedOut(self):
        self.finishedLaunching.emit()

