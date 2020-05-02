# Copyright 2016 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from PyQt5.QtCore import Qt, QSize
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


class DetailsDialog(DetailsDialogBase):
    def __init__(self, parent, app):
        DetailsDialogBase.__init__(self, parent, app)
        self.selectedPixmap = None
        self.referencePixmap = None
        self.scaleFactor = 1.0

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
                "actionNormalSize",
                QKeySequence.Refresh,
                "zoom-normal",
                tr("Normal size"),
                self.zoomNormalSize,
            )
            (
                "actionBestFit",
                QKeySequence.Refresh,
                "zoom-reset",
                tr("Best fit"),
                self.zoomBestFit,
            )
        ]
        createActions(ACTIONS, self)

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
        self.selectedImage = QLabel(self)
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

        self.buttonNormalSize = QToolButton(self.verticalToolBar)
        self.buttonNormalSize.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.buttonNormalSize.setDefaultAction(self.actionNormalSize)
        self.buttonNormalSize.setText('Normal Size')
        self.buttonNormalSize.setIcon(QIcon.fromTheme('zoom-original'))
        self.buttonNormalSize.setEnabled(True)

        self.buttonBestFit = QToolButton(self.verticalToolBar)
        self.buttonBestFit.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.buttonBestFit.setDefaultAction(self.actionZoomReset)
        self.buttonBestFit.setText('BestFit')
        self.buttonBestFit.setIcon(QIcon.fromTheme('zoom-best-fit'))
        self.buttonBestFit.setEnabled(False)

        self.verticalToolBar.addWidget(self.buttonImgSwap)
        self.verticalToolBar.addWidget(self.buttonZoomIn)
        self.verticalToolBar.addWidget(self.buttonZoomOut)
        self.verticalToolBar.addWidget(self.buttonNormalSize)
        self.verticalToolBar.addWidget(self.buttonBestFit)

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
       
        self._resetButtons()

        self._updateImages()

    def _updateImages(self):
        if self.selectedPixmap is not None:
            target_size = self.selectedImage.size()
            if self.scaleFactor > 0:
                scaledPixmap = self.selectedPixmap.scaled(
                    target_size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation) # widget expands here
            else:
                scaledPixmap = self.selectedPixmap.scaled(
                    target_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.selectedImage.setPixmap(scaledPixmap)
            # self.selectedImage.adjustSize()
        else:
            self.selectedImage.setPixmap(QPixmap())
            self.scaleFactor = 1.0

        if self.referencePixmap is not None:
            target_size = self.referenceImage.size()
            if self.scaleFactor > 0:
                scaledPixmap = self.referencePixmap.scaled(
                    target_size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation) # widget expands here
            else:
                scaledPixmap = self.referencePixmap.scaled(
                    target_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.referenceImage.setPixmap(scaledPixmap)
        else:
            self.referenceImage.setPixmap(QPixmap())
            self.scaleFactor = 1.0

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
        self.scaleFactor *= factor 
        print(f'Factor is now = {self.scaleFactor}.')
        self.referenceImage.resize(self.scaleFactor * self.referencePixmap.size())
        self.selectedImage.resize(self.scaleFactor * self.selectedPixmap.size())

        self.buttonZoomIn.setEnabled(self.scaleFactor < 3.0)
        self.buttonZoomOut.setEnabled(self.scaleFactor > 1.0)
        self.buttonBestFit.setEnabled(self.scaleFactor != 1.0)

    def _resetButtons(self):
        self.buttonZoomIn.setEnabled(True)
        self.buttonZoomOut.setEnabled(False)
        self.buttonBestFit.setEnabled(False)

    def swapImages(self):
        # self.horizontalLayout.replaceWidget(self.selectedImage, self.referenceImage)
        self._tempPixmap = self.referencePixmap
        self.referencePixmap = self.selectedPixmap
        self.selectedPixmap = self._tempPixmap
        self._updateImages()
        # swap the columns in the details table as well
        self.tableView.horizontalHeader().swapSections(1, 2)

    def zoomIn(self):
        self.scaleImages(1.25)

    def zoomOut(self):
        self.scaleImages(0.8)

    def zoomNormalSize(self):
        self.scaleFactor = 1.0

    def zoomBestFit(self):
        self.scaleFactor = 1.0
        self.referenceImage.resize(self.scaleFactor * self.referencePixmap.size())
        self.selectedImage.resize(self.scaleFactor * self.selectedPixmap.size())
        self.buttonBestFit.setEnabled(False)
        self.buttonZoomOut.setEnabled(False)
        self.buttonZoomIn.setEnabled(True)
        self._updateImages()

    def imagePan(self):
        pass

# TODO: place handle above table view to drag and resize (splitter?)
# TODO: colorize or bolden values in table views when they differ?
# TODO: double click on details view PATH row opens path in default application