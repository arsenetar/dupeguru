# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from PyQt5.QtCore import (
    QObject, Qt, QSize, QRectF, QPointF, QPoint, pyqtSlot, pyqtSignal, QEvent)
from PyQt5.QtGui import QPixmap, QPainter, QPalette, QCursor, QIcon, QKeySequence
from PyQt5.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem,
    QToolBar, QToolButton, QAction, QWidget, QScrollArea,
    QApplication, QAbstractScrollArea, QStyle)
from hscommon.trans import trget
from hscommon.plat import ISLINUX
tr = trget("ui")

MAX_SCALE = 12.0
MIN_SCALE = 0.1


def createActions(actions, target):
    # actions = [(name, shortcut, icon, desc, func)]
    for name, shortcut, icon, desc, func in actions:
        action = QAction(target)
        if icon:
            action.setIcon(icon)
        if shortcut:
            action.setShortcut(shortcut)
        action.setText(desc)
        action.triggered.connect(func)
        setattr(target, name, action)


class ViewerToolBar(QToolBar):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.parent = parent
        self.controller = controller
        self.setupActions(controller)
        self.createButtons()
        self.buttonImgSwap.setEnabled(False)
        self.buttonZoomIn.setEnabled(False)
        self.buttonZoomOut.setEnabled(False)
        self.buttonNormalSize.setEnabled(False)
        self.buttonBestFit.setEnabled(False)

    def setupActions(self, controller):
        # actions = [(name, shortcut, icon, desc, func)]
        ACTIONS = [
            (
                "actionZoomIn",
                QKeySequence.ZoomIn,
                QIcon.fromTheme("zoom-in")
                if ISLINUX
                and not self.parent.app.prefs.details_dialog_override_theme_icons
                else QIcon(QPixmap(":/" + "zoom_in")),
                tr("Increase zoom"),
                controller.zoomIn,
            ),
            (
                "actionZoomOut",
                QKeySequence.ZoomOut,
                QIcon.fromTheme("zoom-out")
                if ISLINUX
                and not self.parent.app.prefs.details_dialog_override_theme_icons
                else QIcon(QPixmap(":/" + "zoom_out")),
                tr("Decrease zoom"),
                controller.zoomOut,
            ),
            (
                "actionNormalSize",
                tr("Ctrl+/"),
                QIcon.fromTheme("zoom-original")
                if ISLINUX
                and not self.parent.app.prefs.details_dialog_override_theme_icons
                else QIcon(QPixmap(":/" + "zoom_original")),
                tr("Normal size"),
                controller.zoomNormalSize,
            ),
            (
                "actionBestFit",
                tr("Ctrl+*"),
                QIcon.fromTheme("zoom-best-fit")
                if ISLINUX
                and not self.parent.app.prefs.details_dialog_override_theme_icons
                else QIcon(QPixmap(":/" + "zoom_best_fit")),
                tr("Best fit"),
                controller.zoomBestFit,
            )
        ]
        # TODO try with QWidgetAction() instead in order to have
        # the popup menu work in the toolbar (if resized below minimum height)
        createActions(ACTIONS, self)

    def createButtons(self):
        self.buttonImgSwap = QToolButton(self)
        self.buttonImgSwap.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.buttonImgSwap.setIcon(
            QIcon.fromTheme('view-refresh',
                            self.style().standardIcon(QStyle.SP_BrowserReload))
            if ISLINUX
            and not self.parent.app.prefs.details_dialog_override_theme_icons
            else QIcon(QPixmap(":/" + "exchange")))
        self.buttonImgSwap.setText('Swap images')
        self.buttonImgSwap.setToolTip('Swap images')
        self.buttonImgSwap.pressed.connect(self.controller.swapImages)
        self.buttonImgSwap.released.connect(self.controller.swapImages)

        self.buttonZoomIn = QToolButton(self)
        self.buttonZoomIn.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.buttonZoomIn.setDefaultAction(self.actionZoomIn)
        # self.buttonZoomIn.setText('ZoomIn')
        # self.buttonZoomIn.setIcon(QIcon.fromTheme('zoom-in'))
        self.buttonZoomIn.setEnabled(False)

        self.buttonZoomOut = QToolButton(self)
        self.buttonZoomOut.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.buttonZoomOut.setDefaultAction(self.actionZoomOut)
        # self.buttonZoomOut.setText('ZoomOut')
        # self.buttonZoomOut.setIcon(QIcon.fromTheme('zoom-out'))
        self.buttonZoomOut.setEnabled(False)

        self.buttonNormalSize = QToolButton(self)
        self.buttonNormalSize.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.buttonNormalSize.setDefaultAction(self.actionNormalSize)
        # self.buttonNormalSize.setText('Normal Size')
        # self.buttonNormalSize.setIcon(QIcon.fromTheme('zoom-original'))
        self.buttonNormalSize.setEnabled(True)

        self.buttonBestFit = QToolButton(self)
        self.buttonBestFit.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.buttonBestFit.setDefaultAction(self.actionBestFit)
        # self.buttonBestFit.setText('BestFit')
        # self.buttonBestFit.setIcon(QIcon.fromTheme('zoom-best-fit'))
        self.buttonBestFit.setEnabled(False)

        self.addWidget(self.buttonImgSwap)
        self.addWidget(self.buttonZoomIn)
        self.addWidget(self.buttonZoomOut)
        self.addWidget(self.buttonNormalSize)
        self.addWidget(self.buttonBestFit)


class BaseController(QObject):
    """Abstract Base class. Singleton.
    Base proxy interface to keep image viewers synchronized.
    Relays function calls, keep tracks of things."""

    def __init__(self, parent):
        super().__init__()
        self.selectedViewer = None
        self.referenceViewer = None
        # cached pixmaps
        self.selectedPixmap = QPixmap()
        self.referencePixmap = QPixmap()
        self.scaledSelectedPixmap = QPixmap()
        self.scaledReferencePixmap = QPixmap()
        self.current_scale = 1.0
        self.bestFit = True
        self.parent = parent  # To change buttons' states
        self.cached_group = None
        self.same_dimensions = True

    def setupViewers(self, selectedViewer, referenceViewer):
        self.selectedViewer = selectedViewer
        self.referenceViewer = referenceViewer
        self.selectedViewer.controller = self
        self.referenceViewer.controller = self
        self._setupConnections()

    def _setupConnections(self):
        self.selectedViewer.connectMouseSignals()
        self.referenceViewer.connectMouseSignals()

    def updateView(self, ref, dupe, group):
        # To keep current scale accross dupes from the same group
        previous_same_dimensions = self.same_dimensions
        self.same_dimensions = True
        same_group = True
        if group != self.cached_group:
            same_group = False
            self.resetState()
        self.cached_group = group

        self.selectedPixmap = QPixmap(str(dupe.path))
        if ref is dupe:  # currently selected file is the actual reference file
            # self.same_dimensions = False
            self.referencePixmap = QPixmap()
            self.scaledReferencePixmap = QPixmap()
            self.parent.verticalToolBar.buttonImgSwap.setEnabled(False)
            self.parent.verticalToolBar.buttonNormalSize.setEnabled(True)
        else:
            self.referencePixmap = QPixmap(str(ref.path))
            self.parent.verticalToolBar.buttonImgSwap.setEnabled(True)
            if ref.dimensions != dupe.dimensions:
                self.same_dimensions = False
            self.parent.verticalToolBar.buttonNormalSize.setEnabled(True)
        self.updateButtonsAsPerDimensions(previous_same_dimensions)
        self.updateBothImages(same_group)
        self.centerViews(same_group and self.referencePixmap.isNull())

    def updateBothImages(self, same_group=False):
        # WARNING this is called on every resize event,
        ignore_update = self.referencePixmap.isNull()
        if ignore_update:
            self.selectedViewer.ignore_signal = True
        # the SelectedImageViewer widget sometimes ends up being bigger
        # than the ReferenceImageViewer by one pixel, which distorts the
        # scaled down pixmap for the reference, hence we'll reuse its size here.
        selected_size = self._updateImage(
            self.selectedPixmap, self.scaledSelectedPixmap,
            self.selectedViewer, None, same_group)
        self._updateImage(
            self.referencePixmap, self.scaledReferencePixmap,
            self.referenceViewer, selected_size, same_group)
        if ignore_update:
            self.selectedViewer.ignore_signal = False

    def _updateImage(self, pixmap, scaledpixmap, viewer, target_size=None, same_group=False):
        # WARNING this is called on every resize event, might need to split
        # into a separate function depending on the implementation used
        if pixmap.isNull():
            # This should disable the blank widget
            viewer.setImage(pixmap)
            return
        target_size = viewer.size()
        if not viewer.bestFit:
            if same_group:
                viewer.setImage(pixmap)
                return target_size
            # zoomed in state, expand
            # only if not same_group, we need full update
            scaledpixmap = pixmap.scaled(
                target_size, Qt.KeepAspectRatioByExpanding, Qt.FastTransformation)
        else:
            # best fit, keep ratio always
            scaledpixmap = pixmap.scaled(
                target_size, Qt.KeepAspectRatio, Qt.FastTransformation)
        viewer.setImage(scaledpixmap)
        return target_size

    def resetState(self):
        """Only called when the group of dupes has changed. We reset our
        controller internal state and buttons, center view on viewers."""
        self.selectedPixmap = QPixmap()
        self.scaledSelectedPixmap = QPixmap()
        self.referencePixmap = QPixmap()
        self.scaledReferencePixmap = QPixmap()
        self.setBestFit(True)
        self.current_scale = 1.0
        self.selectedViewer.current_scale = 1.0
        self.referenceViewer.current_scale = 1.0
        self.selectedViewer.resetCenter()
        self.referenceViewer.resetCenter()
        self.selectedViewer.scaleAt(1.0)
        self.referenceViewer.scaleAt(1.0)
        self.centerViews()
        self.parent.verticalToolBar.buttonZoomIn.setEnabled(False)
        self.parent.verticalToolBar.buttonZoomOut.setEnabled(False)
        self.parent.verticalToolBar.buttonNormalSize.setEnabled(True)
        self.parent.verticalToolBar.buttonBestFit.setEnabled(False)  # active mode by default

    def resetViewersState(self):
        """No item from the model, disable and clear everything."""
        # only called by the details dialog
        self.selectedPixmap = QPixmap()
        self.scaledSelectedPixmap = QPixmap()
        self.referencePixmap = QPixmap()
        self.scaledReferencePixmap = QPixmap()
        self.setBestFit(True)
        self.current_scale = 1.0
        self.selectedViewer.current_scale = 1.0
        self.referenceViewer.current_scale = 1.0
        self.selectedViewer.resetCenter()
        self.referenceViewer.resetCenter()
        self.selectedViewer.scaleAt(1.0)
        self.referenceViewer.scaleAt(1.0)
        self.centerViews()

        self.parent.verticalToolBar.buttonImgSwap.setEnabled(False)
        self.parent.verticalToolBar.buttonZoomIn.setEnabled(False)
        self.parent.verticalToolBar.buttonZoomOut.setEnabled(False)
        self.parent.verticalToolBar.buttonNormalSize.setEnabled(False)
        self.parent.verticalToolBar.buttonBestFit.setEnabled(False)  # active mode by default

        self.selectedViewer.setImage(self.selectedPixmap)  # null
        self.selectedViewer.setEnabled(False)
        self.referenceViewer.setImage(self.referencePixmap)  # null
        self.referenceViewer.setEnabled(False)

    @pyqtSlot()
    def zoomIn(self):
        self.scaleImagesBy(1.25)

    @pyqtSlot()
    def zoomOut(self):
        self.scaleImagesBy(0.8)

    @pyqtSlot(float)
    def scaleImagesBy(self, factor):
        """Compute new scale from factor and scale."""
        self.current_scale *= factor
        self.selectedViewer.scaleBy(factor)
        self.referenceViewer.scaleBy(factor)
        self.updateButtons()

    @pyqtSlot(float)
    def scaleImagesAt(self, scale):
        """Scale at a pre-computed scale."""
        self.current_scale = scale
        self.selectedViewer.scaleAt(scale)
        self.referenceViewer.scaleAt(scale)
        self.updateButtons()

    def updateButtons(self):
        self.parent.verticalToolBar.buttonZoomIn.setEnabled(self.current_scale < MAX_SCALE)
        self.parent.verticalToolBar.buttonZoomOut.setEnabled(self.current_scale > MIN_SCALE)
        self.parent.verticalToolBar.buttonNormalSize.setEnabled(round(self.current_scale, 1) != 1.0)
        self.parent.verticalToolBar.buttonBestFit.setEnabled(self.bestFit is False)

    def updateButtonsAsPerDimensions(self, previous_same_dimensions):
        if not self.same_dimensions:
            self.parent.verticalToolBar.buttonZoomIn.setEnabled(False)
            self.parent.verticalToolBar.buttonZoomOut.setEnabled(False)
            if not self.bestFit:
                self.zoomBestFit()
                self.parent.verticalToolBar.buttonNormalSize.setEnabled(True)
                if not self.referencePixmap.isNull():
                    self.parent.verticalToolBar.buttonImgSwap.setEnabled(True)
            return
        if not self.bestFit and not previous_same_dimensions:
            self.zoomBestFit()
            self.parent.verticalToolBar.buttonNormalSize.setEnabled(True)
            if self.referencePixmap.isNull():
                self.parent.verticalToolBar.buttonImgSwap.setEnabled(False)

    @pyqtSlot()
    def zoomBestFit(self):
        """Setup before scaling to bestfit"""
        self.setBestFit(True)
        self.current_scale = 1.0
        self.selectedViewer.current_scale = 1.0
        self.referenceViewer.current_scale = 1.0

        self.selectedViewer.scaleAt(1.0)
        self.referenceViewer.scaleAt(1.0)

        self.selectedViewer.resetCenter()
        self.referenceViewer.resetCenter()

        target_size = self._updateImage(
            self.selectedPixmap, self.scaledSelectedPixmap,
            self.selectedViewer, None, True)
        self._updateImage(
            self.referencePixmap, self.scaledReferencePixmap,
            self.referenceViewer, target_size, True)
        self.centerViews()

        self.parent.verticalToolBar.buttonZoomIn.setEnabled(False)
        self.parent.verticalToolBar.buttonZoomOut.setEnabled(False)
        self.parent.verticalToolBar.buttonNormalSize.setEnabled(True)
        self.parent.verticalToolBar.buttonBestFit.setEnabled(False)
        self.parent.verticalToolBar.buttonImgSwap.setEnabled(True)

    def setBestFit(self, value):
        self.bestFit = value
        self.selectedViewer.bestFit = value
        self.referenceViewer.bestFit = value

    @pyqtSlot()
    def zoomNormalSize(self):
        self.setBestFit(False)
        self.current_scale = 1.0

        self.selectedViewer.setImage(self.selectedPixmap)
        self.referenceViewer.setImage(self.referencePixmap)

        self.centerViews()

        self.selectedViewer.scaleToNormalSize()
        self.referenceViewer.scaleToNormalSize()

        if self.same_dimensions:
            self.parent.verticalToolBar.buttonZoomIn.setEnabled(True)
            self.parent.verticalToolBar.buttonZoomOut.setEnabled(True)
        else:
            # we can't allow swapping pixmaps of different dimensions
            self.parent.verticalToolBar.buttonImgSwap.setEnabled(False)
        self.parent.verticalToolBar.buttonNormalSize.setEnabled(False)
        self.parent.verticalToolBar.buttonBestFit.setEnabled(True)

    def centerViews(self, only_selected=False):
        self.selectedViewer.centerViewAndUpdate()
        if only_selected:
            return
        self.referenceViewer.centerViewAndUpdate()

    @pyqtSlot()
    def swapImages(self):
        # swap the columns in the details table as well
        self.parent.tableView.horizontalHeader().swapSections(0, 1)


class QWidgetController(BaseController):
    """Specialized version for QWidget-based viewers."""
    def __init__(self, parent):
        super().__init__(parent)

    def _updateImage(self, *args):
        ret = super()._updateImage(*args)
        # Fix alignment when resizing window
        self.centerViews()
        return ret

    @pyqtSlot(QPointF)
    def onDraggedMouse(self, delta):
        if not self.same_dimensions:
            return
        if self.sender() is self.referenceViewer:
            self.selectedViewer.onDraggedMouse(delta)
        else:
            self.referenceViewer.onDraggedMouse(delta)

    @pyqtSlot()
    def swapImages(self):
        self.selectedViewer._pixmap.swap(self.referenceViewer._pixmap)
        self.selectedViewer.centerViewAndUpdate()
        self.referenceViewer.centerViewAndUpdate()
        super().swapImages()


class ScrollAreaController(BaseController):
    """Specialized version fro QLabel-based viewers."""
    def __init__(self, parent):
        super().__init__(parent)

    def _setupConnections(self):
        super()._setupConnections()
        self.selectedViewer.connectScrollBars()
        self.referenceViewer.connectScrollBars()

    def updateBothImages(self, same_group=False):
        super().updateBothImages(same_group)
        if not self.referenceViewer.isEnabled():
            return
        self.referenceViewer._horizontalScrollBar.setValue(
            self.selectedViewer._horizontalScrollBar.value())
        self.referenceViewer._verticalScrollBar.setValue(
            self.selectedViewer._verticalScrollBar.value())

    @pyqtSlot(QPoint)
    def onDraggedMouse(self, delta):
        self.selectedViewer.ignore_signal = True
        self.referenceViewer.ignore_signal = True

        if self.same_dimensions:
            self.selectedViewer.onDraggedMouse(delta)
            self.referenceViewer.onDraggedMouse(delta)
        else:
            if self.sender() is self.selectedViewer:
                self.selectedViewer.onDraggedMouse(delta)
            else:
                self.referenceViewer.onDraggedMouse(delta)

        self.selectedViewer.ignore_signal = False
        self.referenceViewer.ignore_signal = False

    @pyqtSlot()
    def swapImages(self):
        self.referenceViewer._pixmap.swap(self.selectedViewer._pixmap)
        self.referenceViewer.setCachedPixmap()
        self.selectedViewer.setCachedPixmap()
        super().swapImages()

    @pyqtSlot(float, QPointF)
    def onMouseWheel(self, scale, delta):
        self.scaleImagesAt(scale)
        self.selectedViewer.adjustScrollBarsScaled(delta)
        # Signal from scrollbars will automatically change the other:
        # self.referenceViewer.adjustScrollBarsScaled(delta)

    @pyqtSlot(int)
    def onVScrollBarChanged(self, value):
        if not self.same_dimensions:
            return
        if self.sender() is self.referenceViewer._verticalScrollBar:
            if not self.selectedViewer.ignore_signal:
                self.selectedViewer._verticalScrollBar.setValue(value)
        else:
            if not self.referenceViewer.ignore_signal:
                self.referenceViewer._verticalScrollBar.setValue(value)

    @pyqtSlot(int)
    def onHScrollBarChanged(self, value):
        if not self.same_dimensions:
            return
        if self.sender() is self.referenceViewer._horizontalScrollBar:
            if not self.selectedViewer.ignore_signal:
                self.selectedViewer._horizontalScrollBar.setValue(value)
        else:
            if not self.referenceViewer.ignore_signal:
                self.referenceViewer._horizontalScrollBar.setValue(value)

    @pyqtSlot(float)
    def scaleImagesBy(self, factor):
        super().scaleImagesBy(factor)
        # The other is automatically updated via sigals
        self.selectedViewer.adjustScrollBarsFactor(factor)

    @pyqtSlot()
    def zoomBestFit(self):
        # Disable scrollbars to avoid GridLayout size rounding glitch
        super().zoomBestFit()
        if self.referencePixmap.isNull():
            self.parent.verticalToolBar.buttonImgSwap.setEnabled(False)
        self.selectedViewer.toggleScrollBars()
        self.referenceViewer.toggleScrollBars()


class GraphicsViewController(BaseController):
    """Specialized version fro QGraphicsView-based viewers."""
    def __init__(self, parent):
        super().__init__(parent)

    def _setupConnections(self):
        super()._setupConnections()
        self.selectedViewer.connectScrollBars()
        self.referenceViewer.connectScrollBars()
        # Special case for mouse wheel event conflicting with scrollbar adjustments
        self.selectedViewer.other_viewer = self.referenceViewer
        self.referenceViewer.other_viewer = self.selectedViewer

    @pyqtSlot()
    def syncCenters(self):
        if self.sender() is self.referenceViewer:
            self.selectedViewer.setCenter(self.referenceViewer._centerPoint)
        else:
            self.referenceViewer.setCenter(self.selectedViewer._centerPoint)

    @pyqtSlot(float, QPointF)
    def onMouseWheel(self, factor, newCenter):
        self.current_scale *= factor
        if self.sender() is self.referenceViewer:
            self.selectedViewer.scaleBy(factor)
            self.selectedViewer.setCenter(newCenter)
        else:
            self.referenceViewer.scaleBy(factor)
            self.referenceViewer.setCenter(newCenter)

    @pyqtSlot(int)
    def onVScrollBarChanged(self, value):
        if not self.same_dimensions:
            return
        if self.sender() is self.referenceViewer._verticalScrollBar:
            if not self.selectedViewer.ignore_signal:
                self.selectedViewer._verticalScrollBar.setValue(value)
        else:
            if not self.referenceViewer.ignore_signal:
                self.referenceViewer._verticalScrollBar.setValue(value)

    @pyqtSlot(int)
    def onHScrollBarChanged(self, value):
        if not self.same_dimensions:
            return
        if self.sender() is self.referenceViewer._horizontalScrollBar:
            if not self.selectedViewer.ignore_signal:
                self.selectedViewer._horizontalScrollBar.setValue(value)
        else:
            if not self.referenceViewer.ignore_signal:
                self.referenceViewer._horizontalScrollBar.setValue(value)

    @pyqtSlot()
    def swapImages(self):
        self.referenceViewer._pixmap.swap(self.selectedViewer._pixmap)
        self.referenceViewer.setCachedPixmap()
        self.selectedViewer.setCachedPixmap()
        super().swapImages()

    @pyqtSlot()
    def zoomBestFit(self):
        """Setup before scaling to bestfit"""
        self.setBestFit(True)
        self.current_scale = 1.0
        self.selectedViewer.fitScale()
        self.referenceViewer.fitScale()
        self.parent.verticalToolBar.buttonBestFit.setEnabled(False)
        self.parent.verticalToolBar.buttonZoomOut.setEnabled(False)
        self.parent.verticalToolBar.buttonZoomIn.setEnabled(False)
        self.parent.verticalToolBar.buttonNormalSize.setEnabled(True)
        if not self.referencePixmap.isNull():
            self.parent.verticalToolBar.buttonImgSwap.setEnabled(True)
        # else:
        #     self.referenceViewer.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        #     self.referenceViewer.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def updateView(self, ref, dupe, group):
        # Keep current scale accross dupes from the same group
        previous_same_dimensions = self.same_dimensions
        self.same_dimensions = True
        same_group = True
        if group != self.cached_group:
            same_group = False
            self.resetState()
        self.cached_group = group

        self.selectedPixmap = QPixmap(str(dupe.path))
        if ref is dupe:  # currently selected file is the actual reference file
            self.same_dimensions = False
            self.referencePixmap = QPixmap()
            self.parent.verticalToolBar.buttonImgSwap.setEnabled(False)
            self.parent.verticalToolBar.buttonNormalSize.setEnabled(True)
        else:
            self.referencePixmap = QPixmap(str(ref.path))
            self.parent.verticalToolBar.buttonImgSwap.setEnabled(True)
            if ref.dimensions != dupe.dimensions:
                self.same_dimensions = False
            self.parent.verticalToolBar.buttonNormalSize.setEnabled(True)
        # self.selectedViewer.setImage(self.selectedPixmap)
        # self.referenceViewer.setImage(self.referencePixmap)
        self.updateButtonsAsPerDimensions(previous_same_dimensions)
        self.updateBothImages(same_group)

    def updateBothImages(self, same_group=False):
        """This is called only during resize events and while bestFit."""
        ignore_update = self.referencePixmap.isNull()
        if ignore_update:
            self.selectedViewer.ignore_signal = True

        self._updateFitImage(
            self.selectedPixmap, self.selectedViewer)
        self._updateFitImage(
            self.referencePixmap, self.referenceViewer)

        if ignore_update:
            self.selectedViewer.ignore_signal = False

    def _updateFitImage(self, pixmap, viewer):
        # If not same_group, we need full update"""
        viewer.setImage(pixmap)
        if pixmap.isNull():
            # viewer._item = None
            return
        if viewer.bestFit:
            viewer.fitScale()

    def resetState(self):
        """Only called when the group of dupes has changed. We reset our
        controller internal state and buttons, center view on viewers."""
        self.selectedPixmap = QPixmap()
        self.referencePixmap = QPixmap()
        self.setBestFit(True)
        self.current_scale = 1.0
        self.selectedViewer.current_scale = 1.0
        self.referenceViewer.current_scale = 1.0

        self.selectedViewer.resetCenter()
        self.referenceViewer.resetCenter()

        self.selectedViewer.fitScale()
        self.referenceViewer.fitScale()
        # self.centerViews()
        self.parent.verticalToolBar.buttonZoomIn.setEnabled(False)
        self.parent.verticalToolBar.buttonZoomOut.setEnabled(False)
        self.parent.verticalToolBar.buttonBestFit.setEnabled(False)
        self.parent.verticalToolBar.buttonNormalSize.setEnabled(True)

    def resetViewersState(self):
        """No item from the model, disable and clear everything."""
        # only called by the details dialog
        self.selectedPixmap = QPixmap()
        self.scaledSelectedPixmap = QPixmap()
        self.referencePixmap = QPixmap()
        self.scaledReferencePixmap = QPixmap()
        self.setBestFit(True)
        self.current_scale = 1.0
        self.selectedViewer.current_scale = 1.0
        self.referenceViewer.current_scale = 1.0
        self.selectedViewer.resetCenter()
        self.referenceViewer.resetCenter()
        # self.centerViews()
        self.parent.verticalToolBar.buttonZoomIn.setEnabled(False)
        self.parent.verticalToolBar.buttonZoomOut.setEnabled(False)
        self.parent.verticalToolBar.buttonBestFit.setEnabled(False)
        self.parent.verticalToolBar.buttonImgSwap.setEnabled(False)
        self.parent.verticalToolBar.buttonNormalSize.setEnabled(False)

        self.selectedViewer.setImage(self.selectedPixmap)  # null
        self.selectedViewer.setEnabled(False)
        self.referenceViewer.setImage(self.referencePixmap)  # null
        self.referenceViewer.setEnabled(False)

    @pyqtSlot(float)
    def scaleImagesBy(self, factor):
        self.selectedViewer.updateCenterPoint()
        self.referenceViewer.updateCenterPoint()
        super().scaleImagesBy(factor)
        self.selectedViewer.centerOn(self.selectedViewer._centerPoint)
        # Scrollbars sync themselves here


class QWidgetImageViewer(QWidget):
    """Use a QPixmap, but no scrollbars and no keyboard key sequence for navigation."""
    # FIXME: panning while zoomed-in is broken (due to delta not interpolated right?
    mouseDragged = pyqtSignal(QPointF)
    mouseWheeled = pyqtSignal(float)

    def __init__(self, parent, name=""):
        super().__init__(parent)
        self._app = QApplication
        self._pixmap = QPixmap()
        self._rect = QRectF()
        self._lastMouseClickPoint = QPointF()
        self._mousePanningDelta = QPointF()
        self.current_scale = 1.0
        self._drag = False
        self._dragConnection = None
        self._wheelConnection = None
        self._instance_name = name
        self.bestFit = True
        self.controller = None
        self.setMouseTracking(False)

    def __repr__(self):
        return f'{self._instance_name}'

    def connectMouseSignals(self):
        if not self._dragConnection:
            self._dragConnection = self.mouseDragged.connect(
                self.controller.onDraggedMouse)
        if not self._wheelConnection:
            self._wheelConnection = self.mouseWheeled.connect(
                self.controller.scaleImagesBy)

    def disconnectMouseSignals(self):
        if self._dragConnection:
            self.mouseDragged.disconnect()
            self._dragConnection = None
        if self._wheelConnection:
            self.mouseWheeled.disconnect()
            self._wheelConnection = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.translate(self.rect().center())
        painter.scale(self.current_scale, self.current_scale)
        painter.translate(self._mousePanningDelta)
        painter.drawPixmap(self._rect.topLeft(), self._pixmap)

    def resetCenter(self):
        """ Resets origin """
        # Make sure we are not still panning around
        self._mousePanningDelta = QPointF()
        self.update()

    def changeEvent(self, event):
        if event.type() == QEvent.EnabledChange:
            if self.isEnabled():
                self.connectMouseSignals()
                return
            self.disconnectMouseSignals()

    def contextMenuEvent(self, event):
        """Block parent's (main window) context menu on right click."""
        event.accept()

    def mousePressEvent(self, event):
        if self.bestFit or not self.isEnabled():
            event.ignore()
            return
        if event.button() & (Qt.LeftButton | Qt.MidButton | Qt.RightButton):
            self._drag = True
        else:
            self._drag = False
            event.ignore()
            return

        self._lastMouseClickPoint = event.pos()
        self._app.setOverrideCursor(Qt.ClosedHandCursor)
        self.setMouseTracking(True)
        event.accept()

    def mouseMoveEvent(self, event):
        if self.bestFit or not self.isEnabled():
            event.ignore()
            return

        self._mousePanningDelta += (
            event.pos() - self._lastMouseClickPoint) * 1.0 / self.current_scale
        self._lastMouseClickPoint = event.pos()
        if self._drag:
            self.mouseDragged.emit(self._mousePanningDelta)
            self.update()

    def mouseReleaseEvent(self, event):
        if self.bestFit or not self.isEnabled():
            event.ignore()
            return
        # if event.button() == Qt.LeftButton:
        self._drag = False

        self._app.restoreOverrideCursor()
        self.setMouseTracking(False)

    def wheelEvent(self, event):
        if self.bestFit or not self.controller.same_dimensions or not self.isEnabled():
            event.ignore()
            return

        if event.angleDelta().y() > 0:
            if self.current_scale > MAX_SCALE:
                return
            self.mouseWheeled.emit(1.25)  # zoom-in
        else:
            if self.current_scale < MIN_SCALE:
                return
            self.mouseWheeled.emit(0.8)  # zoom-out

    def setImage(self, pixmap):
        if pixmap.isNull():
            if not self._pixmap.isNull():
                self._pixmap = pixmap
            self.disconnectMouseSignals()
            self.setEnabled(False)
            self.update()
            return
        elif not self.isEnabled():
            self.setEnabled(True)
            self.connectMouseSignals()
        self._pixmap = pixmap

    def centerViewAndUpdate(self):
        self._rect = self._pixmap.rect()
        self._rect.translate(-self._rect.center())
        self.update()

    def shouldBeActive(self):
        return True if not self.pixmap.isNull() else False

    def scaleBy(self, factor):
        self.current_scale *= factor
        self.update()

    def scaleAt(self, scale):
        self.current_scale = scale
        self.update()

    def sizeHint(self):
        return QSize(400, 400)

    @pyqtSlot()
    def scaleToNormalSize(self):
        """Called when the pixmap is set back to original size."""
        self.current_scale = 1.0
        self.update()

    @pyqtSlot(QPointF)
    def onDraggedMouse(self, delta):
        self._mousePanningDelta = delta
        self.update()


class ScalablePixmap(QWidget):
    """Container for a pixmap that scales up very fast, used in ScrollAreaImageViewer."""
    def __init__(self, parent):
        super().__init__(parent)
        self._pixmap = QPixmap()
        self.current_scale = 1.0

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.scale(self.current_scale, self.current_scale)
        # painter.drawPixmap(self.rect().topLeft(), self._pixmap)
        # should be the same as:
        painter.drawPixmap(0, 0, self._pixmap)

    def sizeHint(self):
        return self._pixmap.size() * self.current_scale

    def minimumSizeHint(self):
        return self.sizeHint()


class ScrollAreaImageViewer(QScrollArea):
    """Implementation using a pixmap container in a simple scroll area."""
    mouseDragged = pyqtSignal(QPoint)
    mouseWheeled = pyqtSignal(float, QPointF)

    def __init__(self, parent, name=""):
        super().__init__(parent)
        self._parent = parent
        self._app = QApplication
        self._pixmap = QPixmap()
        self._scaledpixmap = None
        self._rect = QRectF()
        self._lastMouseClickPoint = QPointF()
        self._mousePanningDelta = QPoint()
        self.current_scale = 1.0
        self._drag = False
        self._dragConnection = None
        self._wheelConnection = None
        self._instance_name = name
        self.prefs = parent.app.prefs
        self.bestFit = True
        self.controller = None
        self.label = ScalablePixmap(self)
        # This is to avoid sending signals twice on scrollbar updates
        self.ignore_signal = False
        self.setBackgroundRole(QPalette.Dark)
        self.setWidgetResizable(False)
        self.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.setAlignment(Qt.AlignCenter)
        self._verticalScrollBar = self.verticalScrollBar()
        self._horizontalScrollBar = self.horizontalScrollBar()

        if self.prefs.details_dialog_viewers_show_scrollbars:
            self.toggleScrollBars()
        else:
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setWidget(self.label)
        self.setVisible(True)

    def __repr__(self):
        return f'{self._instance_name}'

    def toggleScrollBars(self, forceOn=False):
        if not self.prefs.details_dialog_viewers_show_scrollbars:
            return
        # Ensure that it's off on the first run
        if self.horizontalScrollBarPolicy() == Qt.ScrollBarAsNeeded:
            if forceOn:
                return
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        else:
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

    def connectMouseSignals(self):
        if not self._dragConnection:
            self._dragConnection = self.mouseDragged.connect(
                self.controller.onDraggedMouse)
        if not self._wheelConnection:
            self._wheelConnection = self.mouseWheeled.connect(
                self.controller.onMouseWheel)

    def disconnectMouseSignals(self):
        if self._dragConnection:
            self.mouseDragged.disconnect()
            self._dragConnection = None
        if self._wheelConnection:
            self.mouseWheeled.disconnect()
            self._wheelConnection = None

    def connectScrollBars(self):
        """Only call once controller is connected."""
        # Cyclic connections are handled by Qt
        self._verticalScrollBar.valueChanged.connect(
            self.controller.onVScrollBarChanged, Qt.UniqueConnection)
        self._horizontalScrollBar.valueChanged.connect(
            self.controller.onHScrollBarChanged, Qt.UniqueConnection)

    def contextMenuEvent(self, event):
        """Block parent's (main window) context menu on right click."""
        # Even though we don't have a context menu right now, and the default
        # contextMenuPolicy is DefaultContextMenu, we leverage that handler to
        # avoid raising the Result window's Actions menu
        event.accept()

    def mousePressEvent(self, event):
        if self.bestFit:
            event.ignore()
            return
        if event.button() & (Qt.LeftButton | Qt.MidButton | Qt.RightButton):
            self._drag = True
        else:
            self._drag = False
            event.ignore()
            return
        self._lastMouseClickPoint = event.pos()
        self._app.setOverrideCursor(Qt.ClosedHandCursor)
        self.setMouseTracking(True)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.bestFit:
            event.ignore()
            return
        if self._drag:
            delta = (event.pos() - self._lastMouseClickPoint)
            self._lastMouseClickPoint = event.pos()
            self.mouseDragged.emit(delta)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.bestFit:
            event.ignore()
            return
        self._drag = False
        self._app.restoreOverrideCursor()
        self.setMouseTracking(False)
        super().mouseReleaseEvent(event)

    def wheelEvent(self, event):
        if self.bestFit or not self.controller.same_dimensions:
            event.ignore()
            return
        oldScale = self.current_scale
        if event.angleDelta().y() > 0:  # zoom-in
            if oldScale < MAX_SCALE:
                self.current_scale *= 1.25
        else:
            if oldScale > MIN_SCALE:  # zoom-out
                self.current_scale *= 0.8
        if oldScale == self.current_scale:
            return

        deltaToPos = (event.position() / oldScale) - (self.label.pos() / oldScale)
        delta = (deltaToPos * self.current_scale) - (deltaToPos * oldScale)
        self.mouseWheeled.emit(self.current_scale, delta)

    def setImage(self, pixmap):
        self._pixmap = pixmap
        self.label._pixmap = pixmap
        self.label.update()
        self.label.adjustSize()
        if pixmap.isNull():
            self.setEnabled(False)
            self.disconnectMouseSignals()
        elif not self.isEnabled():
            self.setEnabled(True)
            self.connectMouseSignals()

    def centerViewAndUpdate(self):
        self._rect = self.label.rect()
        self.label.rect().translate(-self._rect.center())
        self.label.current_scale = self.current_scale
        self.label.update()
        # self.viewport().update()

    def setCachedPixmap(self):
        """In case we have changed the cached pixmap, reset it."""
        self.label._pixmap = self._pixmap
        self.label.update()

    def shouldBeActive(self):
        return True if not self.pixmap.isNull() else False

    def scaleBy(self, factor):
        self.current_scale *= factor
        # factor has to be either 1.25 or 0.8 here
        self.label.resize(self.label.size().__imul__(factor))
        self.label.current_scale = self.current_scale
        self.label.update()

    def scaleAt(self, scale):
        self.current_scale = scale
        self.label.resize(self._pixmap.size().__imul__(scale))
        self.label.current_scale = scale
        self.label.update()
        # self.label.adjustSize()

    def adjustScrollBarsFactor(self, factor):
        """After scaling, no mouse position, default to center."""
        # scrollBar.setMaximum(scrollBar.maximum() - scrollBar.minimum() + scrollBar.pageStep())
        self._horizontalScrollBar.setValue(
            int(factor * self._horizontalScrollBar.value()
                + ((factor - 1) * self._horizontalScrollBar.pageStep() / 2)))
        self._verticalScrollBar.setValue(
            int(factor * self._verticalScrollBar.value()
                + ((factor - 1) * self._verticalScrollBar.pageStep() / 2)))

    def adjustScrollBarsScaled(self, delta):
        """After scaling with the mouse, update relative to mouse position."""
        self._horizontalScrollBar.setValue(
            self._horizontalScrollBar.value() + delta.x())
        self._verticalScrollBar.setValue(
            self._verticalScrollBar.value() + delta.y())

    def adjustScrollBarsAuto(self):
        """After panning, update accordingly."""
        self.horizontalScrollBar().setValue(
            self.horizontalScrollBar().value() - self._mousePanningDelta.x())
        self.verticalScrollBar().setValue(
            self.verticalScrollBar().value() - self._mousePanningDelta.y())

    def adjustScrollBarCentered(self):
        """Just center in the middle."""
        self._horizontalScrollBar.setValue(
            int(self._horizontalScrollBar.maximum() / 2))
        self._verticalScrollBar.setValue(
            int(self._verticalScrollBar.maximum() / 2))

    def resetCenter(self):
        """ Resets origin """
        self._mousePanningDelta = QPoint()
        self.current_scale = 1.0
        # self.scaleAt(1.0)

    def setCenter(self, point):
        self._lastMouseClickPoint = point

    def sizeHint(self):
        return self.viewport().rect().size()

    @pyqtSlot()
    def scaleToNormalSize(self):
        """Called when the pixmap is set back to original size."""
        self.scaleAt(1.0)
        self.ensureWidgetVisible(self.label)  # needed for centering
        self.toggleScrollBars(True)

    @pyqtSlot(QPoint)
    def onDraggedMouse(self, delta):
        """Update position from mouse delta sent by the other panel."""
        self._mousePanningDelta = delta
        # Signal from scrollbars had already synced the values here
        self.adjustScrollBarsAuto()

    # def viewportSizeHint(self):
    #     return self.viewport().rect().size()

    # def changeEvent(self, event):
    #     if event.type() == QEvent.EnabledChange:
    #         print(f"{self} is now {'enabled' if self.isEnabled() else 'disabled'}")


class GraphicsViewViewer(QGraphicsView):
    """Re-Implementation a full-fledged GraphicsView but is a bit buggy."""
    mouseDragged = pyqtSignal()
    mouseWheeled = pyqtSignal(float, QPointF)

    def __init__(self, parent, name=""):
        super().__init__(parent)
        self._parent = parent
        self._app = QApplication
        self._pixmap = QPixmap()
        self._scaledpixmap = None
        self._rect = QRectF()
        self._lastMouseClickPoint = QPointF()
        self._mousePanningDelta = QPointF()
        self._scaleFactor = 1.3
        self.zoomInFactor = self._scaleFactor
        self.zoomOutFactor = 1.0 / self._scaleFactor
        self.current_scale = 1.0
        self._drag = False
        self._dragConnection = None
        self._wheelConnection = None
        self._instance_name = name
        self.prefs = parent.app.prefs
        self.bestFit = True
        self.controller = None
        self._centerPoint = QPointF()
        self.centerOn(self._centerPoint)
        self.other_viewer = None
        # specific to this class
        self._scene = QGraphicsScene()
        self._scene.setBackgroundBrush(Qt.black)
        self._item = QGraphicsPixmapItem()
        self.setScene(self._scene)
        self._scene.addItem(self._item)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        # self.matrix = QTransform()
        self._horizontalScrollBar = self.horizontalScrollBar()
        self._verticalScrollBar = self.verticalScrollBar()
        self.ignore_signal = False

        if self.prefs.details_dialog_viewers_show_scrollbars:
            self.toggleScrollBars()
        else:
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        self.setAlignment(Qt.AlignCenter)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setMouseTracking(True)

    def connectMouseSignals(self):
        if not self._dragConnection:
            self._dragConnection = self.mouseDragged.connect(
                self.controller.syncCenters)
        if not self._wheelConnection:
            self._wheelConnection = self.mouseWheeled.connect(
                self.controller.onMouseWheel)

    def disconnectMouseSignals(self):
        if self._dragConnection:
            self.mouseDragged.disconnect()
            self._dragConnection = None
        if self._wheelConnection:
            self.mouseWheeled.disconnect()
            self._wheelConnection = None

    def connectScrollBars(self):
        """Only call once controller is connected."""
        # Cyclic connections are handled by Qt
        self._verticalScrollBar.valueChanged.connect(
            self.controller.onVScrollBarChanged, Qt.UniqueConnection)
        self._horizontalScrollBar.valueChanged.connect(
            self.controller.onHScrollBarChanged, Qt.UniqueConnection)

    def toggleScrollBars(self, forceOn=False):
        if not self.prefs.details_dialog_viewers_show_scrollbars:
            return
        # Ensure that it's off on the first run
        if self.horizontalScrollBarPolicy() == Qt.ScrollBarAsNeeded:
            if forceOn:
                return
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        else:
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

    def contextMenuEvent(self, event):
        """Block parent's (main window) context menu on right click."""
        event.accept()

    def mousePressEvent(self, event):
        if self.bestFit:
            event.ignore()
            return
        if event.button() & (Qt.LeftButton | Qt.MidButton | Qt.RightButton):
            self._drag = True
        else:
            self._drag = False
            event.ignore()
            return
        self._lastMouseClickPoint = event.pos()
        self._app.setOverrideCursor(Qt.ClosedHandCursor)
        self.setMouseTracking(True)
        # We need to propagate to scrollbars, so we send back up
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if self.bestFit:
            event.ignore()
            return
        self._drag = False
        self._app.restoreOverrideCursor()
        self.setMouseTracking(False)
        self.updateCenterPoint()
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        if self.bestFit:
            event.ignore()
            return
        if self._drag:
            self._lastMouseClickPoint = event.pos()
            # We can simply rely on the scrollbar updating each other here
            # self.mouseDragged.emit()
            self.updateCenterPoint()
            super().mouseMoveEvent(event)

    def updateCenterPoint(self):
        self._centerPoint = self.mapToScene(self.rect().center())

    def wheelEvent(self, event):
        if self.bestFit or MIN_SCALE > self.current_scale > MAX_SCALE or not self.controller.same_dimensions:
            event.ignore()
            return
        pointBeforeScale = QPointF(self.mapToScene(self.mapFromGlobal(QCursor.pos())))
        # Get the original screen centerpoint
        screenCenter = QPointF(self.mapToScene(self.rect().center()))
        if event.angleDelta().y() > 0:
            factor = self.zoomInFactor
        else:
            factor = self.zoomOutFactor
        # Avoid scrollbars conflict:
        self.other_viewer.ignore_signal = True
        self.scaleBy(factor)
        pointAfterScale = QPointF(self.mapToScene(self.mapFromGlobal(QCursor.pos())))
        # Get the offset of how the screen moved
        offset = pointBeforeScale - pointAfterScale
        # Adjust to the new center for correct zooming
        newCenter = screenCenter + offset
        self.setCenter(newCenter)
        self.mouseWheeled.emit(factor, newCenter)
        self.other_viewer.ignore_signal = False

    def setImage(self, pixmap):
        if pixmap.isNull():
            self.ignore_signal = True
        elif self.ignore_signal:
            self.ignore_signal = False
        self._pixmap = pixmap
        self._item.setPixmap(pixmap)
        self.translate(1, 1)

    def centerViewAndUpdate(self):
        # Called from the base controller for Normal Size
        pass

    def setCenter(self, point):
        self._centerPoint = point
        self.centerOn(self._centerPoint)

    def resetCenter(self):
        """ Resets origin """
        self._mousePanningDelta = QPointF()
        self.current_scale = 1.0

    def setNewCenter(self, position):
        self._centerPoint = position
        self.centerOn(self._centerPoint)

    def setCachedPixmap(self):
        """In case we have changed the cached pixmap, reset it."""
        self._item.setPixmap(self._pixmap)
        self._item.update()

    def scaleAt(self, scale):
        # self.current_scale = scale
        if scale == 1.0:
            self.resetScale()
        # self.setTransform( QTransform() )
        self.scale(scale, scale)

    def getScale(self):
        return self.transform().m22()

    def scaleBy(self, factor):
        self.current_scale *= factor
        super().scale(factor, factor)

    def resetScale(self):
        # self.setTransform( QTransform() )
        self.resetTransform()  # probably same as above
        self.setCenter(self.scene().sceneRect().center())

    def fitScale(self):
        self.bestFit = True
        super().fitInView(self._scene.sceneRect(), Qt.KeepAspectRatio)
        self.setNewCenter(self._scene.sceneRect().center())

    @pyqtSlot()
    def scaleToNormalSize(self):
        """Called when the pixmap is set back to original size."""
        self.bestFit = False
        self.scaleAt(1.0)
        self.toggleScrollBars(True)
        self.update()

    def adjustScrollBarsScaled(self, delta):
        """After scaling with the mouse, update relative to mouse position."""
        self._horizontalScrollBar.setValue(
            self._horizontalScrollBar.value() + delta.x())
        self._verticalScrollBar.setValue(
            self._verticalScrollBar.value() + delta.y())

    def sizeHint(self):
        return self.viewport().rect().size()

    def adjustScrollBarsFactor(self, factor):
        """After scaling, no mouse position, default to center."""
        self._horizontalScrollBar.setValue(
            int(factor * self._horizontalScrollBar.value()
                + ((factor - 1) * self._horizontalScrollBar.pageStep() / 2)))
        self._verticalScrollBar.setValue(
            int(factor * self._verticalScrollBar.value()
                + ((factor - 1) * self._verticalScrollBar.pageStep() / 2)))

    def adjustScrollBarsAuto(self):
        """After panning, update accordingly."""
        self.horizontalScrollBar().setValue(
            self.horizontalScrollBar().value() - self._mousePanningDelta.x())
        self.verticalScrollBar().setValue(
            self.verticalScrollBar().value() - self._mousePanningDelta.y())
