# Copyright 2016 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from PyQt5.QtCore import Qt, QSize, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QPixmap, QIcon, QKeySequence
from PyQt5.QtWidgets import (QVBoxLayout, QAbstractItemView, QHBoxLayout,
    QLabel, QSizePolicy, QToolBar, QToolButton, QGridLayout, QStyle, QAction,
    QWidget, QApplication )

from hscommon.trans import trget
from hscommon import desktop
from ..details_dialog import DetailsDialog as DetailsDialogBase
from ..details_table import DetailsTable
from qtlib.util import createActions
from qt.pe.image_viewer import (QWidgetImageViewer, ScrollAreaImageViewer,
    QWidgetImageViewerController, QLabelImageViewerController)
tr = trget("ui")

class DetailsDialog(DetailsDialogBase):
    def __init__(self, parent, app):
        self.vController = None
        super().__init__(parent, app)


    def setupActions(self):
        # (name, shortcut, icon, desc, func)
        ACTIONS = [
            (
                # FIXME probably not used right now
                "actionSwap",
                QKeySequence.Backspace,
                "view-refresh",
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
                "zoom-original",
                tr("Normal size"),
                self.zoomNormalSize,
            ),
            (
                "actionBestFit",
                tr("Ctrl+p"),
                "zoom-best-fit",
                tr("Best fit"),
                self.zoomBestFit,
            )
        ]
        createActions(ACTIONS, self)

    def _setupUi(self):
        self.setupActions()
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

        self.selectedImageViewer = QWidgetImageViewer(
            self, "selectedImage")
        # self.selectedImage = QLabel(self)
        # sizePolicy = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        # sizePolicy.setHorizontalStretch(0)
        # sizePolicy.setVerticalStretch(0)
        # sizePolicy.setHeightForWidth(
        #     self.selectedImage.sizePolicy().hasHeightForWidth()
        # )
        # self.selectedImage.setSizePolicy(sizePolicy)
        # self.selectedImage.setScaledContents(False)
        # self.selectedImage.setAlignment(Qt.AlignCenter)
        # # self.horizontalLayout.addWidget(self.selectedImage)
        self.horizontalLayout.addWidget(self.selectedImageViewer, 0, 0, 3, 1)

        self.verticalToolBar = QToolBar(self)
        self.verticalToolBar.setOrientation(Qt.Orientation(2))
        # self.subVLayout = QVBoxLayout(self)
        # self.subVLayout.addWidget(self.verticalToolBar)
        # self.horizontalLayout.addLayout(self.subVLayout)

        self.buttonImgSwap = QToolButton(self.verticalToolBar)
        self.buttonImgSwap.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.buttonImgSwap.setIcon(QIcon.fromTheme('view-refresh', \
            self.style().standardIcon(QStyle.SP_BrowserReload)))
        self.buttonImgSwap.setText('Swap images')
        self.buttonImgSwap.setToolTip('Swap images')
        self.buttonImgSwap.pressed.connect(self.swapImages)
        self.buttonImgSwap.released.connect(self.deswapImages)

        self.buttonZoomIn = QToolButton(self.verticalToolBar)
        self.buttonZoomIn.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.buttonZoomIn.setDefaultAction(self.actionZoomIn)
        self.buttonZoomIn.setText('ZoomIn')
        self.buttonZoomIn.setIcon(QIcon.fromTheme('zoom-in'))

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
        self.buttonBestFit.setDefaultAction(self.actionBestFit)
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

        self.referenceImageViewer = QWidgetImageViewer(
            self, "referenceImage")
        # self.referenceImage = QLabel(self)
        # sizePolicy = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        # sizePolicy.setHorizontalStretch(0)
        # sizePolicy.setVerticalStretch(0)
        # sizePolicy.setHeightForWidth(
        #     self.referenceImage.sizePolicy().hasHeightForWidth()
        # )
        # self.referenceImage.setSizePolicy(sizePolicy)
        # self.referenceImage.setAlignment(Qt.AlignCenter)
        self.horizontalLayout.addWidget(self.referenceImageViewer, 0, 2, 3, 1)
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

        self.disable_buttons()
        # We use different types of controller depending on the
        # underlying widgets we use to display images
        # because their interface methods might differ
        if isinstance(self.selectedImageViewer, QWidgetImageViewer):
            self.vController = QWidgetImageViewerController(
                            self.selectedImageViewer,
                            self.referenceImageViewer,
                            self)
        elif isinstance(self.selectedImageViewer, ScrollAreaImageViewer):
            self.vController = QLabelImageViewerController(
                            self.selectedImageViewer,
                            self.referenceImageViewer,
                            self)


    def _update(self):
        if not self.app.model.selected_dupes:
            self.clear_all()
            return
        dupe = self.app.model.selected_dupes[0]
        group = self.app.model.results.get_group_of_duplicate(dupe)
        ref = group.ref

        if self.vController is None:
            return
        self.vController.update(ref, dupe)

    def _updateImages(self):
        if not self.vController.bestFit:
            return
        self.vController._updateImages()

    def clear_all(self):
        """No item from the model, disable and clear everything."""
        self.vController.clear_all()

    def disable_buttons(self):
        # FIXME Only called once at startup
        self.buttonImgSwap.setEnabled(False)
        self.buttonZoomIn.setEnabled(False)
        self.buttonZoomOut.setEnabled(False)
        self.buttonNormalSize.setEnabled(False)
        self.buttonBestFit.setEnabled(False)

    # --- Override
    def resizeEvent(self, event):
        if self.vController is None:
            return
        self._updateImages()

    def show(self):
        DetailsDialogBase.show(self)
        self._update()

    # model --> view
    def refresh(self):
        DetailsDialogBase.refresh(self)
        if self.isVisible():
            self._update()

    # ImageViewers
    def scaleImages(self, factor):
        self.vController.scaleImages(factor)

    @pyqtSlot()
    def swapImages(self):
        """Swap pixmaps between ImageViewers."""
        self.vController.swapImages()
        # swap the columns in the details table as well
        self.tableView.horizontalHeader().swapSections(1, 2)

    @pyqtSlot()
    def deswapImages(self):
        """Restore swapped pixmaps between ImageViewers."""
        self.vController.deswapImages()
        # deswap the columns in the details table as well
        self.tableView.horizontalHeader().swapSections(1, 2)

    @pyqtSlot()
    def zoomIn(self):
        self.vController.scaleImages(1.25)

    @pyqtSlot()
    def zoomOut(self):
        self.vController.scaleImages(0.8)

    @pyqtSlot()
    def scale_to_bestfit(self):
        self.vController.scale_to_bestfit()

    @pyqtSlot()
    def zoomBestFit(self):
        self.vController.zoomBestFit()
        self.scale_to_bestfit()

    @pyqtSlot()
    def zoomNormalSize(self):
        self.vController.zoomNormalSize()
