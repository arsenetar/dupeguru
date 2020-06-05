# Copyright 2016 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from PyQt5.QtCore import Qt, QSize, pyqtSlot, pyqtSignal
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
    QAction,
    QWidget,
    QApplication,
)

from hscommon.trans import trget
from hscommon import desktop
from ..details_dialog import DetailsDialog as DetailsDialogBase
from ..details_table import DetailsTable
from qtlib.util import createActions
from qt.pe.image_viewer import ImageViewer
tr = trget("ui")

class DetailsDialog(DetailsDialogBase):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.selectedPixmap = QPixmap()
        self.referencePixmap = QPixmap()
        self.scaledSelectedPixmap = QPixmap()
        self.scaledReferencePixmap = QPixmap()
        self.scaleFactor = 1.0
        self.bestFit = True

    def setupActions(self):
        # (name, shortcut, icon, desc, func)
        ACTIONS = [
            (
                # FIXME probably not used right now
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
            ),
            (
                "actionBestFit",
                tr("Ctrl+p"),
                "zoom-reset",
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

        self.selectedImage = ImageViewer(self, "selectedImage")
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
        self.buttonImgSwap.setToolTip('Swap images')
        self.buttonImgSwap.pressed.connect(self.swapImages)
        self.buttonImgSwap.released.connect(self.deswapImages)

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

        self.referenceImage = ImageViewer(self, "referenceImage")
        # self.referenceImage = QLabel(self)
        # sizePolicy = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        # sizePolicy.setHorizontalStretch(0)
        # sizePolicy.setVerticalStretch(0)
        # sizePolicy.setHeightForWidth(
        #     self.referenceImage.sizePolicy().hasHeightForWidth()
        # )
        # self.referenceImage.setSizePolicy(sizePolicy)
        # self.referenceImage.setAlignment(Qt.AlignCenter)
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

        self.disable_buttons()

    def _update(self):
        print("_update()")
        if not self.app.model.selected_dupes:
            self.clear_all()
            return
        dupe = self.app.model.selected_dupes[0]
        group = self.app.model.results.get_group_of_duplicate(dupe)
        ref = group.ref

        self.resetState()
        self.selectedPixmap = QPixmap(str(dupe.path))
        if ref is dupe: # currently selected file is the ref
            self.referencePixmap = QPixmap()
            self.scaledReferencePixmap = QPixmap()
            self.buttonImgSwap.setEnabled(False)
            # disable the blank widget.
            self.disable_widget(self.referenceImage)
        else:
            self.referencePixmap = QPixmap(str(ref.path))
            self.buttonImgSwap.setEnabled(True)
            self.enable_widget(self.referenceImage)

        self.update_selected_widget()
        self.update_reference_widget()

        self._updateImages()

    def _updateImages(self):
        target_size = None
        if self.selectedPixmap.isNull():
            # self.disable_widget(self.selectedImage, self.referenceImage)
            pass
        else:
            target_size = self.selectedImage.size()
            if not self.bestFit:
                # zoomed in state, expand
                self.scaledSelectedPixmap = self.selectedPixmap.scaled(
                    target_size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            else: 
                # best fit, keep ratio always
                self.scaledSelectedPixmap = self.selectedPixmap.scaled(
                    target_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.selectedImage.setPixmap(self.scaledSelectedPixmap)

        if self.referencePixmap.isNull():
            # self.disable_widget(self.referenceImage, self.selectedImage)
            pass
        else:
            # the selectedImage viewer widget sometimes ends up being bigger
            # than the referenceImage viewer, which distorts by one pixel the
            # scaled down pixmap for the reference, hence we'll reuse its size here.
            # target_size = self.selectedImage.size()
            if not self.bestFit:
                self.scaledReferencePixmap = self.referencePixmap.scaled(
                    target_size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            else:
                self.scaledReferencePixmap = self.referencePixmap.scaled(
                    target_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.referenceImage.setPixmap(self.scaledReferencePixmap)

    def update_selected_widget(self):
        print("update_selected_widget()")
        if not self.selectedPixmap.isNull():
            self.enable_widget(self.selectedImage)
            self.connect_signal(self.selectedImage, self.referenceImage)
        else:
            self.disable_widget(self.selectedImage)
            self.disconnect_signal(self.referenceImage)

    def update_reference_widget(self):
        print("update_reference_widget()")
        if not self.referencePixmap.isNull():
            self.enable_widget(self.referenceImage)
            self.connect_signal(self.referenceImage, self.selectedImage)
        else:
            self.disable_widget(self.referenceImage)
            self.disconnect_signal(self.selectedImage)

    def enable_widget(self, widget):
        """We want to receive signals from the other_widget."""
        print(f"enable_widget({widget})")
        if not widget.isEnabled():
            widget.setEnabled(True)

    def disable_widget(self, widget):
        """Disables this widget and prevents receiving signals from other_widget."""
        print(f"disable_widget({widget})")
        widget.setPixmap(QPixmap())
        widget.setDisabled(True)

    def connect_signal(self, widget, other_widget):
        """We want this widget to send its signal to the other_widget."""
        print(f"connect_signal({widget}, {other_widget})")
        if widget.connection is None:
            if other_widget.isEnabled():
                widget.connection = widget.mouseMoved.connect(other_widget.slot_paint_event)
                print(f"Connected signal from {widget} to slot of {other_widget}")

    def disconnect_signal(self, other_widget):
        """We don't want this widget to send its signal anymore to the other_widget."""
        print(f"disconnect_signal({other_widget}")
        if other_widget.connection:
            other_widget.mouseMoved.disconnect()
            other_widget.connection = None
            print(f"Disconnected signal from {other_widget}")

    def resetState(self):
        self.referencePixmap = QPixmap()
        self.scaledReferencePixmap = QPixmap()
        self.selectedPixmap = QPixmap()
        self.scaledSelectedPixmap = QPixmap()
        self.buttonZoomIn.setEnabled(False)
        self.buttonZoomOut.setEnabled(False)
        self.buttonBestFit.setEnabled(False) # active mode by default
        self.buttonNormalSize.setEnabled(True)
        self.bestFit = True
        self.scaleFactor = 1.0
        self.referenceImage.setCenter()
        self.selectedImage.setCenter()

    def clear_all(self):
        """No item from the model, disable and clear everything."""
        self.resetState()

        self.selectedPixmap = QPixmap()
        self.scaledSelectedPixmap = QPixmap()
        self.selectedImage.setPixmap(QPixmap())
        self.selectedImage.setDisabled(True)

        self.referencePixmap = QPixmap()
        self.scaledReferencePixmap = QPixmap()
        self.referenceImage.setPixmap(QPixmap())
        self.referenceImage.setDisabled(True)

        self.buttonImgSwap.setDisabled(True)
        self.buttonNormalSize.setDisabled(True)

    def disable_buttons(self):
        self.buttonImgSwap.setEnabled(False)
        self.buttonZoomIn.setEnabled(False)
        self.buttonZoomOut.setEnabled(False)
        self.buttonNormalSize.setEnabled(False)
        self.buttonBestFit.setEnabled(False)

    # --- Override
    def resizeEvent(self, event):
        if not self.bestFit:
            return
        self._updateImages()

    def show(self):
        print("show()")
        DetailsDialogBase.show(self)
        self._update()

    # model --> view
    def refresh(self):
        print("refresh()")
        DetailsDialogBase.refresh(self)
        if self.isVisible():
            self._update()

    # ImageViewers
    def scaleImages(self, factor):
        self.scaleFactor *= factor

        print(f'QDialog scaleFactor = {self.scaleFactor} (+factor {factor})')

        self.referenceImage.scale(self.scaleFactor)
        self.selectedImage.scale(self.scaleFactor)

        self.buttonZoomIn.setEnabled(self.scaleFactor < 16.0)
        self.buttonZoomOut.setEnabled(self.scaleFactor > 1.0)
        self.buttonBestFit.setEnabled(self.bestFit is False)
        self.buttonNormalSize.setEnabled(self.scaleFactor != 1.0)

    @pyqtSlot()
    def swapImages(self):
        """Swap pixmaps between ImageViewers."""
        if self.bestFit:
            self.selectedImage.setPixmap(self.scaledReferencePixmap)
            self.referenceImage.setPixmap(self.scaledSelectedPixmap)
        else:
            self.selectedImage.setPixmap(self.referencePixmap)
            self.referenceImage.setPixmap(self.selectedPixmap)

        # swap the columns in the details table as well
        self.tableView.horizontalHeader().swapSections(1, 2)

    @pyqtSlot()
    def deswapImages(self):
        """Restore swapped pixmaps between ImageViewers."""
        if self.bestFit:
            self.selectedImage.setPixmap(self.scaledSelectedPixmap)
            self.referenceImage.setPixmap(self.scaledReferencePixmap)
        else:
            self.selectedImage.setPixmap(self.selectedPixmap)
            self.referenceImage.setPixmap(self.referencePixmap)

        self.tableView.horizontalHeader().swapSections(1, 2)

    @pyqtSlot()
    def zoomIn(self):
        self.scaleImages(1.25)

    @pyqtSlot()
    def zoomOut(self):
        self.scaleImages(0.8)

    @pyqtSlot()
    def scale_to_bestfit(self):
        self.referenceImage.scale(self.scaleFactor)
        self.selectedImage.scale(self.scaleFactor)
        self.referenceImage.setCenter()
        self.selectedImage.setCenter()
        self._updateImages()

    @pyqtSlot()
    def zoomBestFit(self):
        self.bestFit = True
        self.scaleFactor = 1.0
        self.buttonBestFit.setEnabled(False)
        self.buttonZoomOut.setEnabled(False)
        self.buttonZoomIn.setEnabled(False)
        self.buttonNormalSize.setEnabled(True)
        self.scale_to_bestfit()

    @pyqtSlot()
    def zoomNormalSize(self):
        self.bestFit = False
        self.scaleFactor = 1.0

        self.selectedImage.setPixmap(self.selectedPixmap)
        self.referenceImage.setPixmap(self.referencePixmap)

        self.selectedImage.pixmapReset()
        self.referenceImage.pixmapReset()

        self.update_selected_widget()
        self.update_reference_widget()

        self.buttonNormalSize.setEnabled(False)
        self.buttonZoomIn.setEnabled(True)
        self.buttonZoomOut.setEnabled(True)
        self.buttonBestFit.setEnabled(True)
