# Created By: Virgil Dupras
# Created On: 2010-02-05
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDockWidget, QWidget

from .details_table import DetailsModel
from hscommon.plat import ISLINUX


class DetailsDialog(QDockWidget):
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, Qt.Tool, **kwargs)
        self.parent = parent
        self.app = app
        self.model = app.model.details_panel
        self.setAllowedAreas(Qt.AllDockWidgetAreas)
        self._setupUi()
        # To avoid saving uninitialized geometry on appWillSavePrefs, we track whether our dialog
        # has been shown. If it has, we know that our geometry should be saved.
        self._shown_once = False
        self._wasDocked, area = self.app.prefs.restoreGeometry("DetailsWindowRect", self)
        self.tableModel = DetailsModel(self.model, app)
        # tableView is defined in subclasses
        self.tableView.setModel(self.tableModel)
        self.model.view = self
        self.app.willSavePrefs.connect(self.appWillSavePrefs)
        # self.setAttribute(Qt.WA_DeleteOnClose)
        parent.addDockWidget(
            area if self._wasDocked else Qt.BottomDockWidgetArea, self)

    def _setupUi(self):  # Virtual
        pass

    def show(self):
        if not self._shown_once and self._wasDocked:
            self.setFloating(False)
        self._shown_once = True
        super().show()
        self.update_options()

    def update_options(self):
        # This disables the title bar (if we had not set one before already)
        # essentially making it a simple floating window, not dockable anymore
        if not self.app.prefs.details_dialog_titlebar_enabled:
            if not self.titleBarWidget():  # default title bar
                self.setTitleBarWidget(QWidget())  # disables title bar
                # Windows (and MacOS?) users cannot move a floating window which
                # has not native decoration so we force it to dock for now
                if not ISLINUX:
                    self.setFloating(False)
        elif self.titleBarWidget() is not None:  # title bar is disabled
            self.setTitleBarWidget(None)  # resets to the default title bar
        elif not self.titleBarWidget() and not self.app.prefs.details_dialog_titlebar_enabled:
            self.setTitleBarWidget(QWidget())

        features = self.features()
        if self.app.prefs.details_dialog_vertical_titlebar:
            self.setFeatures(features | QDockWidget.DockWidgetVerticalTitleBar)
        elif features & QDockWidget.DockWidgetVerticalTitleBar:
            self.setFeatures(features ^ QDockWidget.DockWidgetVerticalTitleBar)

    # --- Events
    def appWillSavePrefs(self):
        if self._shown_once:
            self.app.prefs.saveGeometry("DetailsWindowRect", self)

    # --- model --> view
    def refresh(self):
        self.tableModel.beginResetModel()
        self.tableModel.endResetModel()
