# Created By: Virgil Dupras
# Created On: 2009-04-25
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from PyQt5.QtCore import Qt, QRect
from PyQt5.QtWidgets import (
    QMainWindow,
    QMenu,
    QLabel,
    QFileDialog,
    QMenuBar,
    QWidget,
    QVBoxLayout,
    QAbstractItemView,
    QStatusBar,
    QDialog,
    QPushButton,
    QCheckBox,
    QDesktopWidget,
)

from hscommon.trans import trget
from qtlib.util import moveToScreenCenter, horizontalWrap, createActions
from qtlib.search_edit import SearchEdit

from core.app import AppMode
from .results_model import ResultsView
from .stats_label import StatsLabel
from .prioritize_dialog import PrioritizeDialog
from .se.results_model import ResultsModel as ResultsModelStandard
from .me.results_model import ResultsModel as ResultsModelMusic
from .pe.results_model import ResultsModel as ResultsModelPicture

tr = trget("ui")


class ResultWindow(QMainWindow):
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, **kwargs)
        self.app = app
        self.specific_actions = set()
        self._setupUi()
        if app.model.app_mode == AppMode.Picture:
            MODEL_CLASS = ResultsModelPicture
        elif app.model.app_mode == AppMode.Music:
            MODEL_CLASS = ResultsModelMusic
        else:
            MODEL_CLASS = ResultsModelStandard
        self.resultsModel = MODEL_CLASS(self.app, self.resultsView)
        self.stats = StatsLabel(app.model.stats_label, self.statusLabel)
        self._update_column_actions_status()

        self.menuColumns.triggered.connect(self.columnToggled)
        self.resultsView.doubleClicked.connect(self.resultsDoubleClicked)
        self.resultsView.spacePressed.connect(self.resultsSpacePressed)
        self.detailsButton.clicked.connect(self.actionDetails.triggered)
        self.dupesOnlyCheckBox.stateChanged.connect(self.powerMarkerTriggered)
        self.deltaValuesCheckBox.stateChanged.connect(self.deltaTriggered)
        self.searchEdit.searchChanged.connect(self.searchChanged)
        self.app.willSavePrefs.connect(self.appWillSavePrefs)

    def _setupActions(self):
        # (name, shortcut, icon, desc, func)
        ACTIONS = [
            ("actionDetails", "Ctrl+I", "", tr("Details"), self.detailsTriggered),
            ("actionActions", "", "", tr("Actions"), self.actionsTriggered),
            (
                "actionPowerMarker",
                "Ctrl+1",
                "",
                tr("Show Dupes Only"),
                self.powerMarkerTriggered,
            ),
            ("actionDelta", "Ctrl+2", "", tr("Show Delta Values"), self.deltaTriggered),
            (
                "actionDeleteMarked",
                "Ctrl+D",
                "",
                tr("Send Marked to Recycle Bin..."),
                self.deleteTriggered,
            ),
            (
                "actionMoveMarked",
                "Ctrl+M",
                "",
                tr("Move Marked to..."),
                self.moveTriggered,
            ),
            (
                "actionCopyMarked",
                "Ctrl+Shift+M",
                "",
                tr("Copy Marked to..."),
                self.copyTriggered,
            ),
            (
                "actionRemoveMarked",
                "Ctrl+R",
                "",
                tr("Remove Marked from Results"),
                self.removeMarkedTriggered,
            ),
            (
                "actionReprioritize",
                "",
                "",
                tr("Re-Prioritize Results..."),
                self.reprioritizeTriggered,
            ),
            (
                "actionRemoveSelected",
                "Ctrl+Del",
                "",
                tr("Remove Selected from Results"),
                self.removeSelectedTriggered,
            ),
            (
                "actionIgnoreSelected",
                "Ctrl+Shift+Del",
                "",
                tr("Add Selected to Ignore List"),
                self.addToIgnoreListTriggered,
            ),
            (
                "actionMakeSelectedReference",
                "Ctrl+Space",
                "",
                tr("Make Selected into Reference"),
                self.app.model.make_selected_reference,
            ),
            (
                "actionOpenSelected",
                "Ctrl+O",
                "",
                tr("Open Selected with Default Application"),
                self.openTriggered,
            ),
            (
                "actionRevealSelected",
                "Ctrl+Shift+O",
                "",
                tr("Open Containing Folder of Selected"),
                self.revealTriggered,
            ),
            (
                "actionRenameSelected",
                "F2",
                "",
                tr("Rename Selected"),
                self.renameTriggered,
            ),
            ("actionMarkAll", "Ctrl+A", "", tr("Mark All"), self.markAllTriggered),
            (
                "actionMarkNone",
                "Ctrl+Shift+A",
                "",
                tr("Mark None"),
                self.markNoneTriggered,
            ),
            (
                "actionInvertMarking",
                "Ctrl+Alt+A",
                "",
                tr("Invert Marking"),
                self.markInvertTriggered,
            ),
            (
                "actionMarkSelected",
                Qt.Key_Space,
                "",
                tr("Mark Selected"),
                self.markSelectedTriggered,
            ),
            (
                "actionExportToHTML",
                "",
                "",
                tr("Export To HTML"),
                self.app.model.export_to_xhtml,
            ),
            (
                "actionExportToCSV",
                "",
                "",
                tr("Export To CSV"),
                self.app.model.export_to_csv,
            ),
            (
                "actionSaveResults",
                "Ctrl+S",
                "",
                tr("Save Results..."),
                self.saveResultsTriggered,
            ),
            (
                "actionInvokeCustomCommand",
                "Ctrl+Alt+I",
                "",
                tr("Invoke Custom Command"),
                self.app.invokeCustomCommand,
            ),
        ]
        createActions(ACTIONS, self)
        self.actionDelta.setCheckable(True)
        self.actionPowerMarker.setCheckable(True)

        if self.app.main_window:  # We use tab widgets in this case
            # Keep track of actions which should only be accessible from this class
            for action, _, _, _, _ in ACTIONS:
                self.specific_actions.add(getattr(self, action))

    def _setupMenu(self):
        if not self.app.use_tabs:
            # we are our own QMainWindow, we need our own menu bar
            self.menubar = QMenuBar()  # self.menuBar() works as well here
            self.menubar.setGeometry(QRect(0, 0, 630, 22))
            self.menuFile = QMenu(self.menubar)
            self.menuFile.setTitle(tr("File"))
            self.menuMark = QMenu(self.menubar)
            self.menuMark.setTitle(tr("Mark"))
            self.menuActions = QMenu(self.menubar)
            self.menuActions.setTitle(tr("Actions"))
            self.menuColumns = QMenu(self.menubar)
            self.menuColumns.setTitle(tr("Columns"))
            self.menuView = QMenu(self.menubar)
            self.menuView.setTitle(tr("View"))
            self.menuHelp = QMenu(self.menubar)
            self.menuHelp.setTitle(tr("Help"))
            self.setMenuBar(self.menubar)
            menubar = self.menubar
        else:
            # we are part of a tab widget, we populate its window's menubar instead
            self.menuFile = self.app.main_window.menuFile
            self.menuMark = self.app.main_window.menuMark
            self.menuActions = self.app.main_window.menuActions
            self.menuColumns = self.app.main_window.menuColumns
            self.menuView = self.app.main_window.menuView
            self.menuHelp = self.app.main_window.menuHelp
            menubar = self.app.main_window.menubar

        self.menuActions.addAction(self.actionDeleteMarked)
        self.menuActions.addAction(self.actionMoveMarked)
        self.menuActions.addAction(self.actionCopyMarked)
        self.menuActions.addAction(self.actionRemoveMarked)
        self.menuActions.addAction(self.actionReprioritize)
        self.menuActions.addSeparator()
        self.menuActions.addAction(self.actionRemoveSelected)
        self.menuActions.addAction(self.actionIgnoreSelected)
        self.menuActions.addAction(self.actionMakeSelectedReference)
        self.menuActions.addSeparator()
        self.menuActions.addAction(self.actionOpenSelected)
        self.menuActions.addAction(self.actionRevealSelected)
        self.menuActions.addAction(self.actionInvokeCustomCommand)
        self.menuActions.addAction(self.actionRenameSelected)
        self.menuMark.addAction(self.actionMarkAll)
        self.menuMark.addAction(self.actionMarkNone)
        self.menuMark.addAction(self.actionInvertMarking)
        self.menuMark.addAction(self.actionMarkSelected)

        self.menuView.addAction(self.actionDetails)
        self.menuView.addSeparator()
        self.menuView.addAction(self.actionPowerMarker)
        self.menuView.addAction(self.actionDelta)
        self.menuView.addSeparator()
        if not self.app.use_tabs:
            self.menuView.addAction(self.app.actionIgnoreList)
        # This also pushes back the options entry to the bottom of the menu
        self.menuView.addSeparator()
        self.menuView.addAction(self.app.actionPreferences)

        self.menuHelp.addAction(self.app.actionShowHelp)
        self.menuHelp.addAction(self.app.actionOpenDebugLog)
        self.menuHelp.addAction(self.app.actionAbout)
        self.menuFile.addAction(self.actionSaveResults)
        self.menuFile.addAction(self.actionExportToHTML)
        self.menuFile.addAction(self.actionExportToCSV)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.app.actionQuit)

        menubar.addAction(self.menuFile.menuAction())
        menubar.addAction(self.menuMark.menuAction())
        menubar.addAction(self.menuActions.menuAction())
        menubar.addAction(self.menuColumns.menuAction())
        menubar.addAction(self.menuView.menuAction())
        menubar.addAction(self.menuHelp.menuAction())

        # Columns menu
        menu = self.menuColumns
        # Avoid adding duplicate actions in tab widget menu in case we recreated
        # the Result Window instance.
        if menu.actions():
            menu.clear()
        self._column_actions = []
        for index, (display, visible) in enumerate(
            self.app.model.result_table.columns.menu_items()
        ):
            action = menu.addAction(display)
            action.setCheckable(True)
            action.setChecked(visible)
            action.item_index = index
            self._column_actions.append(action)
        menu.addSeparator()
        action = menu.addAction(tr("Reset to Defaults"))
        action.item_index = -1

        # Action menu
        actionMenu = QMenu(tr("Actions"), menubar)
        actionMenu.addAction(self.actionDeleteMarked)
        actionMenu.addAction(self.actionMoveMarked)
        actionMenu.addAction(self.actionCopyMarked)
        actionMenu.addAction(self.actionRemoveMarked)
        actionMenu.addSeparator()
        actionMenu.addAction(self.actionRemoveSelected)
        actionMenu.addAction(self.actionIgnoreSelected)
        actionMenu.addAction(self.actionMakeSelectedReference)
        actionMenu.addSeparator()
        actionMenu.addAction(self.actionOpenSelected)
        actionMenu.addAction(self.actionRevealSelected)
        actionMenu.addAction(self.actionInvokeCustomCommand)
        actionMenu.addAction(self.actionRenameSelected)
        self.actionActions.setMenu(actionMenu)
        self.actionsButton.setMenu(self.actionActions.menu())

    def _setupUi(self):
        self.setWindowTitle(tr("{} Results").format(self.app.NAME))
        self.resize(630, 514)
        self.centralwidget = QWidget(self)
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.actionsButton = QPushButton(tr("Actions"))
        self.detailsButton = QPushButton(tr("Details"))
        self.dupesOnlyCheckBox = QCheckBox(tr("Dupes Only"))
        self.deltaValuesCheckBox = QCheckBox(tr("Delta Values"))
        self.searchEdit = SearchEdit()
        self.searchEdit.setMaximumWidth(300)
        self.horizontalLayout = horizontalWrap(
            [
                self.actionsButton,
                self.detailsButton,
                self.dupesOnlyCheckBox,
                self.deltaValuesCheckBox,
                None,
                self.searchEdit,
                8,
            ]
        )
        self.horizontalLayout.setSpacing(8)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.resultsView = ResultsView(self.centralwidget)
        self.resultsView.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.resultsView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.resultsView.setSortingEnabled(True)
        self.resultsView.setWordWrap(False)
        self.resultsView.verticalHeader().setVisible(False)
        h = self.resultsView.horizontalHeader()
        h.setHighlightSections(False)
        h.setSectionsMovable(True)
        h.setStretchLastSection(False)
        h.setDefaultAlignment(Qt.AlignLeft)
        self.verticalLayout.addWidget(self.resultsView)
        self.setCentralWidget(self.centralwidget)
        self._setupActions()
        self._setupMenu()
        self.statusbar = QStatusBar(self)
        self.statusbar.setSizeGripEnabled(True)
        self.setStatusBar(self.statusbar)
        self.statusLabel = QLabel(self)
        self.statusbar.addPermanentWidget(self.statusLabel, 1)

        if self.app.prefs.resultWindowIsMaximized:
            self.setWindowState(self.windowState() | Qt.WindowMaximized)
        else:
            if self.app.prefs.resultWindowRect is not None:
                self.setGeometry(self.app.prefs.resultWindowRect)
                # if not on any screen move to center of default screen
                # moves to center of closest screen if partially off screen
                frame = self.frameGeometry()
                if QDesktopWidget().screenNumber(self) == -1:
                    moveToScreenCenter(self)
                elif QDesktopWidget().availableGeometry(self).contains(frame) is False:
                    frame.moveCenter(QDesktopWidget().availableGeometry(self).center())
                    self.move(frame.topLeft())
            else:
                moveToScreenCenter(self)

    # --- Private
    def _update_column_actions_status(self):
        # Update menu checked state
        menu_items = self.app.model.result_table.columns.menu_items()
        for action, (display, visible) in zip(self._column_actions, menu_items):
            action.setChecked(visible)

    # --- Actions
    def actionsTriggered(self):
        self.actionsButton.showMenu()

    def addToIgnoreListTriggered(self):
        self.app.model.add_selected_to_ignore_list()

    def copyTriggered(self):
        self.app.model.copy_or_move_marked(True)

    def deleteTriggered(self):
        self.app.model.delete_marked()

    def deltaTriggered(self, state=None):
        # The sender can be either the action or the checkbox, but both have a isChecked() method.
        self.resultsModel.delta_values = self.sender().isChecked()
        self.actionDelta.setChecked(self.resultsModel.delta_values)
        self.deltaValuesCheckBox.setChecked(self.resultsModel.delta_values)

    def detailsTriggered(self):
        self.app.show_details()

    def markAllTriggered(self):
        self.app.model.mark_all()

    def markInvertTriggered(self):
        self.app.model.mark_invert()

    def markNoneTriggered(self):
        self.app.model.mark_none()

    def markSelectedTriggered(self):
        self.app.model.toggle_selected_mark_state()

    def moveTriggered(self):
        self.app.model.copy_or_move_marked(False)

    def openTriggered(self):
        self.app.model.open_selected()

    def powerMarkerTriggered(self, state=None):
        # see deltaTriggered
        self.resultsModel.power_marker = self.sender().isChecked()
        self.actionPowerMarker.setChecked(self.resultsModel.power_marker)
        self.dupesOnlyCheckBox.setChecked(self.resultsModel.power_marker)

    def preferencesTriggered(self):
        self.app.show_preferences()

    def removeMarkedTriggered(self):
        self.app.model.remove_marked()

    def removeSelectedTriggered(self):
        self.app.model.remove_selected()

    def renameTriggered(self):
        index = self.resultsView.selectionModel().currentIndex()
        # Our index is the current row, with column set to 0. Our filename column is 1 and that's
        # what we want.
        index = index.sibling(index.row(), 1)
        self.resultsView.edit(index)

    def reprioritizeTriggered(self):
        dlg = PrioritizeDialog(self, self.app)
        result = dlg.exec()
        if result == QDialog.Accepted:
            dlg.model.perform_reprioritization()

    def revealTriggered(self):
        self.app.model.reveal_selected()

    def saveResultsTriggered(self):
        title = tr("Select a file to save your results to")
        files = tr("dupeGuru Results (*.dupeguru)")
        destination, chosen_filter = QFileDialog.getSaveFileName(self, title, "", files)
        if destination:
            if not destination.endswith(".dupeguru"):
                destination = "{}.dupeguru".format(destination)
            self.app.model.save_as(destination)
            self.app.recentResults.insertItem(destination)

    # --- Events
    def appWillSavePrefs(self):
        prefs = self.app.prefs
        prefs.resultWindowIsMaximized = self.isMaximized()
        prefs.resultWindowRect = self.geometry()

    def columnToggled(self, action):
        index = action.item_index
        if index == -1:
            self.app.model.result_table.columns.reset_to_defaults()
            self._update_column_actions_status()
        else:
            visible = self.app.model.result_table.columns.toggle_menu_item(index)
            action.setChecked(visible)

    def contextMenuEvent(self, event):
        self.actionActions.menu().exec_(event.globalPos())

    def resultsDoubleClicked(self, modelIndex):
        self.app.model.open_selected()

    def resultsSpacePressed(self):
        self.app.model.toggle_selected_mark_state()

    def searchChanged(self):
        self.app.model.apply_filter(self.searchEdit.text())

    def closeEvent(self, event):
        # this saves the location of the results window when it is closed
        self.appWillSavePrefs()
