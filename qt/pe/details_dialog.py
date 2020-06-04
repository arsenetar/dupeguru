# Copyright 2016 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from PyQt5.QtCore import Qt, QSize, QRectF, QPointF, pyqtSlot
from PyQt5.QtGui import QPixmap, QIcon, QKeySequence, QPainter, QPalette
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
    QScrollArea,
    QApplication,
    QAbstractScrollArea
)

from hscommon.trans import trget
from hscommon import desktop
from ..details_dialog import DetailsDialog as DetailsDialogBase
from ..details_table import DetailsTable
from qtlib.util import createActions

tr = trget("ui")

class ImageViewer(QWidget):
    """ Displays image and allow manipulations """
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.app = QApplication
        self.pixmap = QPixmap()
        self.m_rect = QRectF()
        self.reference = QPointF()
        self.delta = QPointF()
        self.scalefactor = 1.0

        self.area = QScrollArea(parent)
        self.area.setBackgroundRole(QPalette.Dark)
        self.area.setWidgetResizable(True)
        self.area.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        # self.area.viewport().setAttribute(Qt.WA_StaticContents)

        self.label = QLabel()
        sizePolicy = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setBackgroundRole(QPalette.Base)
        self.label.setSizePolicy(sizePolicy)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setScaledContents(True)

        self.area.setWidget(self.label)
        self.area.setVisible(False)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.translate(self.rect().center())
        painter.scale(self.scalefactor, self.scalefactor)
        painter.translate(self.delta)
        painter.drawPixmap(self.m_rect.topLeft(), self.pixmap)

    def mousePressEvent(self, event):
        if self.parent.bestFit:
            event.ignore() # probably not needed
            return

        self.reference = event.pos()
        self.app.setOverrideCursor(Qt.ClosedHandCursor)
        self.setMouseTracking(True)

    def mouseMoveEvent(self, event):
        if self.parent.bestFit:
            event.ignore() # probably not needed
            return

        self.delta += (event.pos() - self.reference) * 1.0/self.scalefactor
        self.reference = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        if self.parent.bestFit:
            event.ignore() # probably not needed
            return

        self.app.restoreOverrideCursor()
        self.setMouseTracking(False)

    def wheelEvent(self, event):
        if self.parent.bestFit:
            event.ignore() # probably not needed
            return

        if event.angleDelta().y() > 0:
            self.parent.zoomIn()
        else:
            self.parent.zoomOut()

    def setPixmap(self, pixmap):
        self.pixmap = pixmap
        if pixmap is None:
            return
        self.m_rect = self.pixmap.rect()
        self.m_rect.translate(-self.m_rect.center())
        self.update()

    def scale(self, factor):
        self.scalefactor = factor
        print(f"ImaveViewer.scalefactor={self.scalefactor}")
        # self.label.resize(self.scalefactor * self.label.size())
        self.update()

    def sizeHint(self):
        return QSize(400, 400)

    @pyqtSlot()
    def pixmapReset(self):
        self.scalefactor = 1.0
        self.update()


class DetailsDialog(DetailsDialogBase):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.selectedPixmap = None
        self.referencePixmap = None
        self.scaledSelectedPixmap = None
        self.scaledReferencePixmap = None
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

        self.selectedImage = ImageViewer(self)
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

        self.referenceImage = ImageViewer(self)
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

    def _update(self):
        if not self.app.model.selected_dupes:
            return
        dupe = self.app.model.selected_dupes[0]
        group = self.app.model.results.get_group_of_duplicate(dupe)
        ref = group.ref

        self.resetState()
        self.selectedPixmap = QPixmap(str(dupe.path))
        if ref is dupe:
            self.referencePixmap = None
            self.scaledReferencePixmap = None
            self.buttonImgSwap.setEnabled(False)
        else:
            self.referencePixmap = QPixmap(str(ref.path))
            self.buttonImgSwap.setEnabled(True)

        self._updateImages()

    def _updateImages(self):
        target_size = None
        if self.selectedPixmap is not None:
            target_size = self.selectedImage.size()
            if not self.bestFit:
                # zoomed in state, expand
                self.scaledSelectedPixmap = self.selectedPixmap.scaled(
                    target_size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            else: # best fit, keep ratio always
                self.scaledSelectedPixmap = self.selectedPixmap.scaled(
                    target_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.selectedImage.setPixmap(self.scaledSelectedPixmap)
            # self.selectedImage.adjustSize()
        else:
            self.selectedImage.setPixmap(QPixmap())

        if self.referencePixmap is not None:
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
        else:
            self.referenceImage.setPixmap(QPixmap())

    # --- Override
    def resizeEvent(self, event):
        if not self.bestFit:
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

    def resetState(self):
        self.scaledReferencePixmap = None
        self.scaledSelectedPixmapPixmap = None
        self.buttonZoomIn.setEnabled(False)
        self.buttonZoomOut.setEnabled(False)
        self.buttonBestFit.setEnabled(False) # active mode by default
        self.buttonNormalSize.setEnabled(True)
        self.bestFit = True
        self.scaleFactor = 1.0

    def scaleImages(self, factor):
        self.scaleFactor *= factor
        print(f'QDialog scaleFactor = {self.scaleFactor} (+factor {factor})')

        # returns QSize, not good anymore
        # self.referenceImage.scale(self.scaleFactor * self.referencePixmap.size())
        # self.selectedImage.scale(self.scaleFactor * self.selectedPixmap.size())

        self.referenceImage.scale(self.scaleFactor)
        self.selectedImage.scale(self.scaleFactor)

        self.buttonZoomIn.setEnabled(self.scaleFactor < 6.0)
        self.buttonZoomOut.setEnabled(self.scaleFactor > 1.0)
        self.buttonBestFit.setEnabled(self.bestFit is False)
        self.buttonNormalSize.setEnabled(self.scaleFactor != 1.0)

    @pyqtSlot()
    def swapImages(self):
        """ Swap pixmaps between ImageViewers """
        # self.horizontalLayout.replaceWidget(self.selectedImage, self.referenceImage)

        # self._tempPixmap = self.referencePixmap
        # referencePixmap = self.selectedPixmap
        # self.selectedPixmap = self._tempPixmap
        # self._updateImages()

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
        """ Restore swapped pixmaps """
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

        if self.referencePixmap is None:
            self.referenceImage.setPixmap(QPixmap())
        else:
            self.referenceImage.setPixmap(self.referencePixmap)

        self.selectedImage.pixmapReset()
        self.referenceImage.pixmapReset()
        # self.referenceImage.label.resize(self.scaleFactor * self.referencePixmap.size())
        # self.selectedImage.label.resize(self.scaleFactor * self.selectedPixmap.size())
        # self.referenceImage.label.adjustSize()
        # self.selectedImage.label.adjustSize()

        self.buttonNormalSize.setEnabled(False)
        self.buttonZoomIn.setEnabled(True)
        self.buttonZoomOut.setEnabled(True)
        self.buttonBestFit.setEnabled(True)
        # self._updateImages()

