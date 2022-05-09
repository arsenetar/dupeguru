# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from PyQt5.QtCore import QRect, pyqtSlot, Qt, QEvent
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QMainWindow,
    QTabWidget,
    QMenu,
    QTabBar,
    QStackedWidget,
)
from hscommon.trans import trget
from qt.util import move_to_screen_center, create_actions
from qt.directories_dialog import DirectoriesDialog
from qt.result_window import ResultWindow
from qt.ignore_list_dialog import IgnoreListDialog
from qt.exclude_list_dialog import ExcludeListDialog

tr = trget("ui")


class TabWindow(QMainWindow):
    def __init__(self, app, **kwargs):
        super().__init__(None, **kwargs)
        self.app = app
        self.pages = {}  # This is currently not used anywhere
        self.menubar = None
        self.menuList = set()
        self.last_index = -1
        self.previous_widget_actions = set()
        self._setupUi()
        self.app.willSavePrefs.connect(self.appWillSavePrefs)

    def _setupActions(self):
        # (name, shortcut, icon, desc, func)
        ACTIONS = [
            (
                "actionToggleTabs",
                "",
                "",
                tr("Show tab bar"),
                self.toggleTabBar,
            ),
        ]
        create_actions(ACTIONS, self)
        self.actionToggleTabs.setCheckable(True)
        self.actionToggleTabs.setChecked(True)

    def _setupUi(self):
        self.setWindowTitle(self.app.NAME)
        self.resize(640, 480)
        self.tabWidget = QTabWidget()
        # self.tabWidget.setTabPosition(QTabWidget.South)
        self.tabWidget.setContentsMargins(0, 0, 0, 0)
        # self.tabWidget.setTabBarAutoHide(True)
        # This gets rid of the annoying margin around the TabWidget:
        self.tabWidget.setDocumentMode(True)

        self._setupActions()
        self._setupMenu()
        # This should be the same as self.centralWidget.setLayout(self.verticalLayout)
        self.verticalLayout = QVBoxLayout(self.tabWidget)
        # self.verticalLayout.addWidget(self.tabWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.tabWidget.setTabsClosable(True)
        self.setCentralWidget(self.tabWidget)  # only for QMainWindow

        self.tabWidget.currentChanged.connect(self.updateMenuBar)
        self.tabWidget.tabCloseRequested.connect(self.onTabCloseRequested)
        self.updateMenuBar(self.tabWidget.currentIndex())
        self.restoreGeometry()

    def restoreGeometry(self):
        if self.app.prefs.mainWindowRect is not None:
            self.setGeometry(self.app.prefs.mainWindowRect)
        if self.app.prefs.mainWindowIsMaximized:
            self.showMaximized()

    def _setupMenu(self):
        """Setup the menubar boiler plates which will be filled by the underlying
        tab's widgets whenever they are instantiated."""
        self.menubar = self.menuBar()  # QMainWindow, similar to just QMenuBar() here
        # self.setMenuBar(self.menubar)  # already set if QMainWindow class
        self.menubar.setGeometry(QRect(0, 0, 100, 22))
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

        self.menuView.addAction(self.actionToggleTabs)
        self.menuView.addSeparator()

        self.menuList.add(self.menuFile)
        self.menuList.add(self.menuMark)
        self.menuList.add(self.menuActions)
        self.menuList.add(self.menuColumns)
        self.menuList.add(self.menuView)
        self.menuList.add(self.menuHelp)

    @pyqtSlot(int)
    def updateMenuBar(self, page_index=-1):
        if page_index < 0:
            return
        current_index = self.getCurrentIndex()
        active_widget = self.getWidgetAtIndex(current_index)
        if self.last_index < 0:
            self.last_index = current_index
            self.previous_widget_actions = active_widget.specific_actions
            return

        page_type = type(active_widget).__name__
        for menu in self.menuList:
            if menu is self.menuColumns or menu is self.menuActions or menu is self.menuMark:
                if not isinstance(active_widget, ResultWindow):
                    menu.setEnabled(False)
                    continue
                else:
                    menu.setEnabled(True)
            for action in menu.actions():
                if action not in active_widget.specific_actions:
                    if action in self.previous_widget_actions:
                        action.setEnabled(False)
                    continue
                action.setEnabled(True)

        self.app.directories_dialog.actionShowResultsWindow.setEnabled(
            False if page_type == "ResultWindow" else self.app.resultWindow is not None
        )
        self.app.actionIgnoreList.setEnabled(
            True if self.app.ignoreListDialog is not None and not page_type == "IgnoreListDialog" else False
        )
        self.app.actionDirectoriesWindow.setEnabled(False if page_type == "DirectoriesDialog" else True)
        self.app.actionExcludeList.setEnabled(
            True if self.app.excludeListDialog is not None and not page_type == "ExcludeListDialog" else False
        )

        self.previous_widget_actions = active_widget.specific_actions
        self.last_index = current_index

    def createPage(self, cls, **kwargs):
        app = kwargs.get("app", self.app)
        page = None
        if cls == "DirectoriesDialog":
            page = DirectoriesDialog(app)
        elif cls == "ResultWindow":
            parent = kwargs.get("parent", self)
            page = ResultWindow(parent, app)
        elif cls == "IgnoreListDialog":
            parent = kwargs.get("parent", self)
            model = kwargs.get("model")
            page = IgnoreListDialog(parent, model)
            page.accepted.connect(self.onDialogAccepted)
        elif cls == "ExcludeListDialog":
            app = kwargs.get("app", app)
            parent = kwargs.get("parent", self)
            model = kwargs.get("model")
            page = ExcludeListDialog(app, parent, model)
            page.accepted.connect(self.onDialogAccepted)
        self.pages[cls] = page  # Not used, might remove
        return page

    def addTab(self, page, title, switch=False):
        # Warning: this supposedly takes ownership of the page
        index = self.tabWidget.addTab(page, title)
        if isinstance(page, DirectoriesDialog):
            self.tabWidget.tabBar().setTabButton(index, QTabBar.RightSide, None)
        if switch:
            self.setCurrentIndex(index)
        return index

    def showTab(self, page):
        index = self.indexOfWidget(page)
        self.setCurrentIndex(index)

    def indexOfWidget(self, widget):
        return self.tabWidget.indexOf(widget)

    def setCurrentIndex(self, index):
        return self.tabWidget.setCurrentIndex(index)

    def removeTab(self, index):
        return self.tabWidget.removeTab(index)

    def isTabVisible(self, index):
        return self.tabWidget.isTabVisible(index)

    def getCurrentIndex(self):
        return self.tabWidget.currentIndex()

    def getWidgetAtIndex(self, index):
        return self.tabWidget.widget(index)

    def getCount(self):
        return self.tabWidget.count()

    # --- Events
    def appWillSavePrefs(self):
        # Right now this is useless since the first spawned dialog inside the
        # QTabWidget will assign its geometry after restoring it
        prefs = self.app.prefs
        prefs.mainWindowIsMaximized = self.isMaximized()
        if not self.isMaximized():
            prefs.mainWindowRect = self.geometry()

    def showEvent(self, event):
        if not self.isMaximized():
            # have to do this here as the frameGeometry is not correct until shown
            move_to_screen_center(self)
        super().showEvent(event)

    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange and not self.isMaximized():
            move_to_screen_center(self)
        super().changeEvent(event)

    def closeEvent(self, close_event):
        # Force closing of our tabbed widgets in reverse order so that the
        # directories dialog (which usually is at index 0) will be called last
        for index in range(self.getCount() - 1, -1, -1):
            self.getWidgetAtIndex(index).closeEvent(close_event)
        self.appWillSavePrefs()

    @pyqtSlot(int)
    def onTabCloseRequested(self, index):
        current_widget = self.getWidgetAtIndex(index)
        if isinstance(current_widget, DirectoriesDialog):
            # if we close this one, the application quits. Force user to use the
            # menu or shortcut. But this is useless if we don't have a button
            # set up to make a close request anyway. This check could be removed.
            return
        self.removeTab(index)

    @pyqtSlot()
    def onDialogAccepted(self):
        """Remove tabbed dialog when Accepted/Done (close button clicked)."""
        widget = self.sender()
        index = self.indexOfWidget(widget)
        if index > -1:
            self.removeTab(index)

    @pyqtSlot()
    def toggleTabBar(self):
        value = self.sender().isChecked()
        self.actionToggleTabs.setChecked(value)
        self.tabWidget.tabBar().setVisible(value)


class TabBarWindow(TabWindow):
    """Implementation which uses a separate QTabBar and QStackedWidget.
    The Tab bar is placed next to the menu bar to save real estate."""

    def __init__(self, app, **kwargs):
        super().__init__(app, **kwargs)

    def _setupUi(self):
        self.setWindowTitle(self.app.NAME)
        self.resize(640, 480)
        self.tabBar = QTabBar()
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self._setupActions()
        self._setupMenu()

        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)
        self.stackedWidget = QStackedWidget()
        self.centralWidget.setLayout(self.verticalLayout)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.addWidget(self.menubar, 0, Qt.AlignTop)
        self.horizontalLayout.addWidget(self.tabBar, 0, Qt.AlignTop)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout.addWidget(self.stackedWidget)

        self.tabBar.currentChanged.connect(self.showTabIndex)
        self.tabBar.tabCloseRequested.connect(self.onTabCloseRequested)

        self.stackedWidget.currentChanged.connect(self.updateMenuBar)
        self.stackedWidget.widgetRemoved.connect(self.onRemovedWidget)

        self.tabBar.setTabsClosable(True)
        self.restoreGeometry()

    def addTab(self, page, title, switch=True):
        stack_index = self.stackedWidget.addWidget(page)
        self.tabBar.insertTab(stack_index, title)

        if isinstance(page, DirectoriesDialog):
            self.tabBar.setTabButton(stack_index, QTabBar.RightSide, None)
        if switch:  # switch to the added tab immediately upon creation
            self.setTabIndex(stack_index)
        return stack_index

    @pyqtSlot(int)
    def showTabIndex(self, index):
        # The tab bar's indices should be aligned with the stackwidget's
        if index >= 0 and index <= self.stackedWidget.count():
            self.stackedWidget.setCurrentIndex(index)

    def indexOfWidget(self, widget):
        # Warning: this may return -1 if widget is not a child of stackedwidget
        return self.stackedWidget.indexOf(widget)

    def setCurrentIndex(self, tab_index):
        self.setTabIndex(tab_index)
        # The signal will handle switching the stackwidget's widget
        # self.stackedWidget.setCurrentWidget(self.stackedWidget.widget(tab_index))

    def setCurrentWidget(self, widget):
        """Sets the current Tab on TabBar for this widget."""
        self.tabBar.setCurrentIndex(self.indexOfWidget(widget))

    @pyqtSlot(int)
    def setTabIndex(self, index):
        if index is None:
            return
        self.tabBar.setCurrentIndex(index)

    @pyqtSlot(int)
    def onRemovedWidget(self, index):
        self.removeTab(index)

    @pyqtSlot(int)
    def removeTab(self, index):
        """Remove the tab, but not the widget (it should already be removed)"""
        return self.tabBar.removeTab(index)

    @pyqtSlot(int)
    def removeWidget(self, widget):
        return self.stackedWidget.removeWidget(widget)

    def isTabVisible(self, index):
        return self.tabBar.isTabVisible(index)

    def getCurrentIndex(self):
        return self.stackedWidget.currentIndex()

    def getWidgetAtIndex(self, index):
        return self.stackedWidget.widget(index)

    def getCount(self):
        return self.stackedWidget.count()

    @pyqtSlot()
    def toggleTabBar(self):
        value = self.sender().isChecked()
        self.actionToggleTabs.setChecked(value)
        self.tabBar.setVisible(value)

    @pyqtSlot(int)
    def onTabCloseRequested(self, index):
        target_widget = self.getWidgetAtIndex(index)
        if isinstance(target_widget, DirectoriesDialog):
            # On MacOS, the tab has a close button even though we explicitely
            # set it to None in order to hide it. This should prevent
            # the "Directories" tab from closing by mistake.
            return
        # target_widget.close()  # seems unnecessary
        # Removing the widget should trigger tab removal via the signal
        self.removeWidget(self.getWidgetAtIndex(index))

    @pyqtSlot()
    def onDialogAccepted(self):
        """Remove tabbed dialog when Accepted/Done (close button clicked)."""
        widget = self.sender()
        self.removeWidget(widget)
