# Copyright 2016 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from PyQt5.QtCore import QRect, Qt
from PyQt5.QtWidgets import (
    QListView,
    QWidget,
    QFileDialog,
    QHeaderView,
    QVBoxLayout,
    QHBoxLayout,
    QTreeView,
    QAbstractItemView,
    QSpacerItem,
    QSizePolicy,
    QPushButton,
    QMainWindow,
    QMenuBar,
    QMenu,
    QLabel,
    QComboBox,
)
from PyQt5.QtGui import QPixmap, QIcon

from hscommon.trans import trget
from core.app import AppMode
from qt.radio_box import RadioBox
from qt.recent import Recent
from qt.util import move_to_screen_center, create_actions

from qt import platform
from qt.directories_model import DirectoriesModel, DirectoriesDelegate

tr = trget("ui")


class DirectoriesDialog(QMainWindow):
    def __init__(self, app, **kwargs):
        super().__init__(None, **kwargs)
        self.app = app
        self.specific_actions = set()
        self.lastAddedFolder = platform.INITIAL_FOLDER_IN_DIALOGS
        self.recentFolders = Recent(self.app, "recentFolders")
        self._setupUi()
        self._updateScanTypeList()
        self.directoriesModel = DirectoriesModel(self.app.model.directory_tree, view=self.treeView)
        self.directoriesDelegate = DirectoriesDelegate()
        self.treeView.setItemDelegate(self.directoriesDelegate)
        self._setupColumns()
        self.app.recentResults.addMenu(self.menuLoadRecent)
        self.app.recentResults.addMenu(self.menuRecentResults)
        self.recentFolders.addMenu(self.menuRecentFolders)
        self._updateAddButton()
        self._updateRemoveButton()
        self._updateLoadResultsButton()
        self._updateActionsState()
        self._setupBindings()

    def _setupBindings(self):
        self.appModeRadioBox.itemSelected.connect(self.appModeButtonSelected)
        self.showPreferencesButton.clicked.connect(self.app.actionPreferences.trigger)
        self.scanButton.clicked.connect(self.scanButtonClicked)
        self.loadResultsButton.clicked.connect(self.actionLoadResults.trigger)
        self.addFolderButton.clicked.connect(self.actionAddFolder.trigger)
        self.removeFolderButton.clicked.connect(self.removeFolderButtonClicked)
        self.treeView.selectionModel().selectionChanged.connect(self.selectionChanged)
        self.app.recentResults.itemsChanged.connect(self._updateLoadResultsButton)
        self.recentFolders.itemsChanged.connect(self._updateAddButton)
        self.recentFolders.mustOpenItem.connect(self.app.model.add_directory)
        self.directoriesModel.foldersAdded.connect(self.directoriesModelAddedFolders)
        self.app.willSavePrefs.connect(self.appWillSavePrefs)

    def _setupActions(self):
        # (name, shortcut, icon, desc, func)
        ACTIONS = [
            (
                "actionLoadResults",
                "Ctrl+L",
                "",
                tr("Load Results..."),
                self.loadResultsTriggered,
            ),
            (
                "actionShowResultsWindow",
                "",
                "",
                tr("Scan Results"),
                self.app.showResultsWindow,
            ),
            ("actionAddFolder", "", "", tr("Add Folder..."), self.addFolderTriggered),
            ("actionLoadDirectories", "", "", tr("Load Directories..."), self.loadDirectoriesTriggered),
            ("actionSaveDirectories", "", "", tr("Save Directories..."), self.saveDirectoriesTriggered),
        ]
        create_actions(ACTIONS, self)
        if self.app.use_tabs:
            # Keep track of actions which should only be accessible from this window
            self.specific_actions.add(self.actionLoadDirectories)
            self.specific_actions.add(self.actionSaveDirectories)

    def _setupMenu(self):
        if not self.app.use_tabs:
            # we are our own QMainWindow, we need our own menu bar
            self.menubar = QMenuBar(self)
            self.menubar.setGeometry(QRect(0, 0, 42, 22))
            self.menuFile = QMenu(self.menubar)
            self.menuFile.setTitle(tr("File"))
            self.menuView = QMenu(self.menubar)
            self.menuView.setTitle(tr("View"))
            self.menuHelp = QMenu(self.menubar)
            self.menuHelp.setTitle(tr("Help"))
            self.setMenuBar(self.menubar)
            menubar = self.menubar
        else:
            # we are part of a tab widget, we populate its window's menubar instead
            self.menuFile = self.app.main_window.menuFile
            self.menuView = self.app.main_window.menuView
            self.menuHelp = self.app.main_window.menuHelp
            menubar = self.app.main_window.menubar

        self.menuLoadRecent = QMenu(self.menuFile)
        self.menuLoadRecent.setTitle(tr("Load Recent Results"))

        self.menuFile.addAction(self.actionLoadResults)
        self.menuFile.addAction(self.menuLoadRecent.menuAction())
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.app.actionClearCache)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionLoadDirectories)
        self.menuFile.addAction(self.actionSaveDirectories)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.app.actionQuit)

        self.menuView.addAction(self.app.actionDirectoriesWindow)
        self.menuView.addAction(self.actionShowResultsWindow)
        self.menuView.addAction(self.app.actionIgnoreList)
        self.menuView.addAction(self.app.actionExcludeList)
        self.menuView.addSeparator()
        self.menuView.addAction(self.app.actionPreferences)

        self.menuHelp.addAction(self.app.actionShowHelp)
        self.menuHelp.addAction(self.app.actionOpenDebugLog)
        self.menuHelp.addAction(self.app.actionAbout)

        menubar.addAction(self.menuFile.menuAction())
        menubar.addAction(self.menuView.menuAction())
        menubar.addAction(self.menuHelp.menuAction())

        # Recent folders menu
        self.menuRecentFolders = QMenu()
        self.menuRecentFolders.addAction(self.actionAddFolder)
        self.menuRecentFolders.addSeparator()

        # Recent results menu
        self.menuRecentResults = QMenu()
        self.menuRecentResults.addAction(self.actionLoadResults)
        self.menuRecentResults.addSeparator()

    def _setupUi(self):
        self.setWindowTitle(self.app.NAME)
        self.resize(420, 338)
        self.centralwidget = QWidget(self)
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setContentsMargins(4, 0, 4, 0)
        self.verticalLayout.setSpacing(0)
        hl = QHBoxLayout()
        label = QLabel(tr("Application Mode:"), self)
        label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        hl.addWidget(label)
        self.appModeRadioBox = RadioBox(self, items=[tr("Standard"), tr("Music"), tr("Picture")], spread=False)
        hl.addWidget(self.appModeRadioBox)
        self.verticalLayout.addLayout(hl)
        hl = QHBoxLayout()
        hl.setAlignment(Qt.AlignLeft)
        label = QLabel(tr("Scan Type:"), self)
        label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        hl.addWidget(label)
        self.scanTypeComboBox = QComboBox(self)
        self.scanTypeComboBox.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed))
        self.scanTypeComboBox.setMaximumWidth(400)
        hl.addWidget(self.scanTypeComboBox)
        self.showPreferencesButton = QPushButton(tr("More Options"), self.centralwidget)
        self.showPreferencesButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        hl.addWidget(self.showPreferencesButton)
        self.verticalLayout.addLayout(hl)
        self.promptLabel = QLabel(tr('Select folders to scan and press "Scan".'), self.centralwidget)
        self.verticalLayout.addWidget(self.promptLabel)
        self.treeView = QTreeView(self.centralwidget)
        self.treeView.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.treeView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.treeView.setAcceptDrops(True)
        triggers = (
            QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed | QAbstractItemView.SelectedClicked
        )
        self.treeView.setEditTriggers(triggers)
        self.treeView.setDragDropOverwriteMode(True)
        self.treeView.setDragDropMode(QAbstractItemView.DropOnly)
        self.treeView.setUniformRowHeights(True)
        self.verticalLayout.addWidget(self.treeView)
        self.horizontalLayout = QHBoxLayout()
        self.removeFolderButton = QPushButton(self.centralwidget)
        self.removeFolderButton.setIcon(QIcon(QPixmap(":/minus")))
        self.removeFolderButton.setShortcut("Del")
        self.horizontalLayout.addWidget(self.removeFolderButton)
        self.addFolderButton = QPushButton(self.centralwidget)
        self.addFolderButton.setIcon(QIcon(QPixmap(":/plus")))
        self.horizontalLayout.addWidget(self.addFolderButton)
        spacer_item = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacer_item)
        self.loadResultsButton = QPushButton(self.centralwidget)
        self.loadResultsButton.setText(tr("Load Results"))
        self.horizontalLayout.addWidget(self.loadResultsButton)
        self.scanButton = QPushButton(self.centralwidget)
        self.scanButton.setText(tr("Scan"))
        self.scanButton.setDefault(True)
        self.horizontalLayout.addWidget(self.scanButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.setCentralWidget(self.centralwidget)

        self._setupActions()
        self._setupMenu()

        if self.app.prefs.directoriesWindowRect is not None:
            self.setGeometry(self.app.prefs.directoriesWindowRect)
        else:
            move_to_screen_center(self)

    def _setupColumns(self):
        header = self.treeView.header()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.resizeSection(1, 100)

    def _updateActionsState(self):
        self.actionShowResultsWindow.setEnabled(self.app.resultWindow is not None)

    def _updateAddButton(self):
        if self.recentFolders.isEmpty():
            self.addFolderButton.setMenu(None)
        else:
            self.addFolderButton.setMenu(self.menuRecentFolders)

    def _updateRemoveButton(self):
        indexes = self.treeView.selectedIndexes()
        if not indexes:
            self.removeFolderButton.setEnabled(False)
            return
        self.removeFolderButton.setEnabled(True)

    def _updateLoadResultsButton(self):
        if self.app.recentResults.isEmpty():
            self.loadResultsButton.setMenu(None)
        else:
            self.loadResultsButton.setMenu(self.menuRecentResults)

    def _updateScanTypeList(self):
        try:
            self.scanTypeComboBox.currentIndexChanged[int].disconnect(self.scanTypeChanged)
        except TypeError:
            # Not connected, ignore
            pass
        self.scanTypeComboBox.clear()
        scan_options = self.app.model.SCANNER_CLASS.get_scan_options()
        for scan_option in scan_options:
            self.scanTypeComboBox.addItem(scan_option.label)
        SCAN_TYPE_ORDER = [so.scan_type for so in scan_options]
        selected_scan_type = self.app.prefs.get_scan_type(self.app.model.app_mode)
        scan_type_index = SCAN_TYPE_ORDER.index(selected_scan_type)
        self.scanTypeComboBox.setCurrentIndex(scan_type_index)
        self.scanTypeComboBox.currentIndexChanged[int].connect(self.scanTypeChanged)
        self.app._update_options()

    # --- QWidget overrides
    def closeEvent(self, event):
        event.accept()
        if self.app.model.results.is_modified:
            title = tr("Unsaved results")
            msg = tr("You have unsaved results, do you really want to quit?")
            if not self.app.confirm(title, msg):
                event.ignore()
        if event.isAccepted():
            self.app.shutdown()

    # --- Events
    def addFolderTriggered(self):
        no_native = not self.app.prefs.use_native_dialogs
        title = tr("Select a folder to add to the scanning list")
        file_dialog = QFileDialog(self, title, self.lastAddedFolder)
        file_dialog.setFileMode(QFileDialog.DirectoryOnly)
        file_dialog.setOption(QFileDialog.DontUseNativeDialog, no_native)
        if no_native:
            file_view = file_dialog.findChild(QListView, "listView")
            if file_view:
                file_view.setSelectionMode(QAbstractItemView.MultiSelection)
            f_tree_view = file_dialog.findChild(QTreeView)
            if f_tree_view:
                f_tree_view.setSelectionMode(QAbstractItemView.MultiSelection)
        if not file_dialog.exec():
            return

        paths = file_dialog.selectedFiles()
        self.lastAddedFolder = paths[-1]
        [self.app.model.add_directory(path) for path in paths]
        [self.recentFolders.insertItem(path) for path in paths]

    def appModeButtonSelected(self, index):
        if index == 2:
            mode = AppMode.PICTURE
        elif index == 1:
            mode = AppMode.MUSIC
        else:
            mode = AppMode.STANDARD
        self.app.model.app_mode = mode
        self._updateScanTypeList()

    def appWillSavePrefs(self):
        self.app.prefs.directoriesWindowRect = self.geometry()

    def directoriesModelAddedFolders(self, folders):
        for folder in folders:
            self.recentFolders.insertItem(folder)

    def loadResultsTriggered(self):
        title = tr("Select a results file to load")
        files = ";;".join([tr("dupeGuru Results (*.dupeguru)"), tr("All Files (*.*)")])
        destination = QFileDialog.getOpenFileName(self, title, "", files)[0]
        if destination:
            self.app.model.load_from(destination)
            self.app.recentResults.insertItem(destination)

    def loadDirectoriesTriggered(self):
        title = tr("Select a directories file to load")
        files = ";;".join([tr("dupeGuru Directories (*.dupegurudirs)"), tr("All Files (*.*)")])
        destination = QFileDialog.getOpenFileName(self, title, "", files)[0]
        if destination:
            self.app.model.load_directories(destination)

    def removeFolderButtonClicked(self):
        self.directoriesModel.model.remove_selected()

    def saveDirectoriesTriggered(self):
        title = tr("Select a file to save your directories to")
        files = tr("dupeGuru Directories (*.dupegurudirs)")
        destination, chosen_filter = QFileDialog.getSaveFileName(self, title, "", files)
        if destination:
            if not destination.endswith(".dupegurudirs"):
                destination = f"{destination}.dupegurudirs"
            self.app.model.save_directories_as(destination)

    def scanButtonClicked(self):
        if self.app.model.results.is_modified:
            title = tr("Start a new scan")
            msg = tr("You have unsaved results, do you really want to continue?")
            if not self.app.confirm(title, msg):
                return
        self.app.model.start_scanning(self.app.prefs.profile_scan)

    def scanTypeChanged(self, index):
        scan_options = self.app.model.SCANNER_CLASS.get_scan_options()
        self.app.prefs.set_scan_type(self.app.model.app_mode, scan_options[index].scan_type)
        self.app._update_options()

    def selectionChanged(self, selected, deselected):
        self._updateRemoveButton()
