# Copyright 2016 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from PyQt5.QtCore import Qt, QSize, pyqtSignal, QModelIndex
from PyQt5.QtGui import QPixmap, QIcon, QKeySequence
from PyQt5.QtWidgets import (
    QVBoxLayout,
    QAbstractItemView,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QToolBar,
    QToolButton,
    QGridLayout,
    QStyle,
    QAction
)

from hscommon.trans import trget
from hscommon import desktop
from ..details_dialog import DetailsDialog as DetailsDialogBase
from ..details_table import DetailsTable
from qtlib.util import createActions

tr = trget("ui")

class ClickableLabel(QLabel):
    def __init__(self, parent):
        QLabel.__init__(self, parent)
        self.path = ""

    def mouseDoubleClickEvent(self, event):
        self.doubleClicked.emit()

    doubleClicked = pyqtSignal()

class DetailsDialog(DetailsDialogBase):
    def __init__(self, parent, app):
        DetailsDialogBase.__init__(self, parent, app)
        self.selectedPixmap = None
        self.referencePixmap = None
        self.scaleFactor = 0

    def _setupActions(self):
        # (name, shortcut, icon, desc, func)
        ACTIONS = [
            (
                "actionSwap",
                QKeySequence.Backspace,
                "swap",
                tr("Swap images"),
                self.swapImages,
            ),
            (
                "actionZoomIn",
                QKeySequence.ZoomIn,
                "zoom-in",
                tr("Increase zoom factor"),
                self.zoomIn,
            ),
            (
                "actionZoomOut",
                QKeySequence.ZoomOut,
                "zoom-out",
                tr("Decrease zoom factor"),
                self.zoomOut,
            ),
            (
                "actionZoomReset",
                QKeySequence.Refresh,
                "zoom-reset",
                tr("Reset zoom factor"),
                self.zoomReset,
            )
        ]
        createActions(ACTIONS, self)

        # special case as it resets when button is released
        # self.actionSwap = QAction(self)
        # # self.actionSwap.setIcon(QIcon(QPixmap()))
        # self.actionSwap.setShortcut(QKeySequence.Backspace)
        # self.actionSwap.setText(tr("Swap images"))
        # self.actionSwap.pressed.connect(self.swapImages)

    def _setupUi(self):
        self._setupActions()
        self.setWindowTitle(tr("Details"))
        self.resize(502, 295)
        self.setMinimumSize(QSize(250, 250))
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        # self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout = QGridLayout()
        self.horizontalLayout.setColumnMinimumWidth(1, 30)
        self.horizontalLayout.setColumnStretch(0,1)
        self.horizontalLayout.setColumnStretch(1,0)
        self.horizontalLayout.setColumnStretch(2,1)
        self.horizontalLayout.setSpacing(4)
        self.selectedImage = ClickableLabel(self)
        sizePolicy = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.selectedImage.sizePolicy().hasHeightForWidth()
        )
        self.selectedImage.setSizePolicy(sizePolicy)
        self.selectedImage.setScaledContents(False)
        self.selectedImage.setAlignment(Qt.AlignCenter)
        # self.horizontalLayout.addWidget(self.selectedImage)
        self.selectedImage.doubleClicked.connect(self.mouseDoubleClickedEvent)
        self.horizontalLayout.addWidget(self.selectedImage, 0, 0, 3, 1)

        self.verticalToolBar = QToolBar(self)
        self.verticalToolBar.setOrientation(Qt.Orientation(2))
        # self.subVLayout = QVBoxLayout(self)
        # self.subVLayout.addWidget(self.verticalToolBar)
        # self.horizontalLayout.addLayout(self.subVLayout)

        self.buttonImgSwap = QToolButton(self.verticalToolBar)
        self.buttonImgSwap.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.buttonImgSwap.setIcon(QIcon.fromTheme('document-revert', \
            self.style().standardIcon(QStyle.SP_BrowserReload)))
        self.buttonImgSwap.setText('Swap images')
        self.buttonImgSwap.pressed.connect(self.swapImages)
        self.buttonImgSwap.released.connect(self.swapImages)

        self.buttonZoomIn = QToolButton(self.verticalToolBar)
        self.buttonZoomIn.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.buttonZoomIn.setDefaultAction(self.actionZoomIn)
        self.buttonZoomIn.setText('ZoomIn')
        self.buttonZoomIn.setIcon(QIcon.fromTheme(('zoom-in'), QIcon(":images/zoom-in.png")))

        self.buttonZoomOut = QToolButton(self.verticalToolBar)
        self.buttonZoomOut.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.buttonZoomOut.setDefaultAction(self.actionZoomOut)
        self.buttonZoomOut.setText('ZoomOut')
        self.buttonZoomOut.setIcon(QIcon.fromTheme('zoom-out'))
        self.buttonZoomOut.setEnabled(False)

        self.buttonResetZoom = QToolButton(self.verticalToolBar)
        self.buttonResetZoom.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.buttonResetZoom.setDefaultAction(self.actionZoomReset)
        self.buttonResetZoom.setText('ResetZoom')
        self.buttonResetZoom.setIcon(QIcon.fromTheme('zoom-original'))
        self.buttonResetZoom.setEnabled(False)

        self.verticalToolBar.addWidget(self.buttonImgSwap)
        self.verticalToolBar.addWidget(self.buttonZoomIn)
        self.verticalToolBar.addWidget(self.buttonZoomOut)
        self.verticalToolBar.addWidget(self.buttonResetZoom)

        self.horizontalLayout.addWidget(self.verticalToolBar, 1, 1, 1, 1, Qt.AlignCenter)
        # self.horizontalLayout.addWidget(self.verticalToolBar, Qt.AlignVCenter)

        self.referenceImage = QLabel(self)
        sizePolicy = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.referenceImage.sizePolicy().hasHeightForWidth()
        )
        self.referenceImage.setSizePolicy(sizePolicy)
        self.referenceImage.setAlignment(Qt.AlignCenter)
        self.horizontalLayout.addWidget(self.referenceImage, 0, 2, 3, 1)
        # self.horizontalLayout.addWidget(self.referenceImage)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.tableView = DetailsTable(self)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableView.sizePolicy().hasHeightForWidth())
        self.tableView.setSizePolicy(sizePolicy)
        self.tableView.setMinimumSize(QSize(0, 188))
        self.tableView.setMaximumSize(QSize(16777215, 190))
        self.tableView.setAlternatingRowColors(True)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableView.setShowGrid(False)
        self.verticalLayout.addWidget(self.tableView)

    def _update(self):
        self._updateButtons()
        if not self.app.model.selected_dupes:
            return
        dupe = self.app.model.selected_dupes[0]
        group = self.app.model.results.get_group_of_duplicate(dupe)
        ref = group.ref

        self.selectedPixmap = QPixmap(str(dupe.path))
        if ref is dupe:
            self.referencePixmap = None
            self.buttonImgSwap.setEnabled(False)
        else:
            self.referencePixmap = QPixmap(str(ref.path))
            self.buttonImgSwap.setEnabled(True)
        self.scaleFactor = 0
        
        self._updateButtons()
        self._updateImages()

    def _updateButtons(self):
        if 0 < self.scaleFactor < 10:
            self.buttonZoomIn.setEnabled(True)
            self.buttonZoomOut.setEnabled(True)
            self.buttonResetZoom.setEnabled(True)
        elif self.scaleFactor >= 10:
            self.buttonZoomIn.setEnabled(False)
        else: # scaleFactor == 0
            self.buttonZoomIn.setEnabled(True)
            self.buttonZoomOut.setEnabled(False)
            self.buttonResetZoom.setEnabled(False)

    def _updateImages(self):
        if self.selectedPixmap is not None:
            target_size = self.selectedImage.size()
            if self.scaleFactor:
                scaledPixmap = self.selectedPixmap.scaled(
                    target_size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation) # widget expands here
            else:
                scaledPixmap = self.selectedPixmap.scaled(
                    target_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.selectedImage.setPixmap(scaledPixmap)
        else:
            self.selectedImage.setPixmap(QPixmap())
            self.scaleFactor = 0

        if self.referencePixmap is not None:
            target_size = self.referenceImage.size()
            if self.scaleFactor:
                scaledPixmap = self.referencePixmap.scaled(
                    target_size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation) # widget expands here
            else:
                scaledPixmap = self.referencePixmap.scaled(
                    target_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.referenceImage.setPixmap(scaledPixmap)
        else:
            self.referenceImage.setPixmap(QPixmap())
            self.scaleFactor = 0

    # --- Override
    def resizeEvent(self, event):
        self._updateImages()

    def show(self):
        DetailsDialogBase.show(self)
        self._update()

    # model --> view
    def refresh(self):
        DetailsDialogBase.refresh(self)
        if self.isVisible():
            self._update()

    def scaleImages(self, factor):
        self.scaleFactor += factor 
        print(f'Factor is now = {self.scaleFactor}.')
        self._updateButtons()

    def swapImages(self):
        # self.horizontalLayout.replaceWidget(self.selectedImage, self.referenceImage)
        self._tempPixmap = self.referencePixmap
        self.referencePixmap = self.selectedPixmap
        self.selectedPixmap = self._tempPixmap
        self._updateImages()
        # swap the columns in the details table as well
        self.tableView.horizontalHeader().swapSections(1, 2)

    def zoomIn(self):
        if self.scaleFactor >= 10: # clamping to x10
            return
        print("ZoomIN")
        self.scaleImages(1)

    def zoomOut(self):
        if self.scaleFactor <= 0:
            return
        print("ZoomOut")
        self.scaleImages(-1)

    def zoomReset(self):
        print("ZoomReset")
        self.scaleFactor = 0
        self.buttonResetZoom.setEnabled(False)
        self.buttonZoomOut.setEnabled(False)
        self.buttonZoomIn.setEnabled(True)
        self._updateImages()

    def imagePan(self):
        pass
    
    def mouseDoubleClickedEvent(self, path):
        desktop.open_path(path)

# TODO: open default application when double click on label
# TODO: place handle above table view to drag and resize (splitter?)
# TODO: colorize or bolden values in table views when they differ?