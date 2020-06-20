# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from PyQt5.QtCore import QObject, Qt, QSize, QRectF, QPointF, QPoint, pyqtSlot, pyqtSignal, QEvent
from PyQt5.QtGui import QPixmap, QPainter, QPalette, QCursor
from PyQt5.QtWidgets import ( QLabel, QSizePolicy, QWidget, QScrollArea,
                              QScrollBar, QApplication, QAbstractScrollArea )

#TODO QWidget version: fix panning while zoomed-in
#TODO: add keyboard shortcuts

class BaseController(QObject):
    """Abstract Base class. Singleton.
    Base proxy interface to keep image viewers synchronized.
    Relays function calls, keep tracks of things."""

    def __init__(self, selectedViewer, referenceViewer, parent):
        super().__init__()
        self.selectedViewer = selectedViewer
        self.referenceViewer = referenceViewer
        self.selectedViewer.controller = self
        self.referenceViewer.controller = self
        self._setupConnections()
        # cached pixmaps
        self.selectedPixmap = QPixmap()
        self.referencePixmap = QPixmap()
        self.scaledSelectedPixmap = QPixmap()
        self.scaledReferencePixmap = QPixmap()
        self.current_scale = 1.0
        self.bestFit = True
        self.wantScrollBars = True
        self.parent = parent #To change buttons' states

    def _setupConnections(self):
        self.selectedViewer.connectMouseSignals()
        self.referenceViewer.connectMouseSignals()

    def update(self, ref, dupe):
        self.resetState()
        self.selectedPixmap = QPixmap(str(dupe.path))
        if ref is dupe: # currently selected file is the actual reference file
            self.referencePixmap = QPixmap()
            self.scaledReferencePixmap = QPixmap()
            self.parent.buttonImgSwap.setEnabled(False)
            # disable the blank widget.
            self.referenceViewer.setImage(self.referencePixmap)
        else:
            self.referencePixmap = QPixmap(str(ref.path))
            self.parent.buttonImgSwap.setEnabled(True)

        self._updateImages()

    def _updateImages(self):
        target_size = None
        if not self.selectedPixmap.isNull():
            target_size = self.selectedViewer.size()
            if not self.bestFit:
                # zoomed in state, expand
                self.scaledSelectedPixmap = self.selectedPixmap.scaled(
                    target_size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            else:
                # best fit, keep ratio always
                self.scaledSelectedPixmap = self.selectedPixmap.scaled(
                    target_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.selectedViewer.setImage(self.scaledSelectedPixmap)
            self.selectedViewer.centerViewAndUpdate()

        if not self.referencePixmap.isNull():
            # the selectedImage viewer widget sometimes ends up being bigger
            # than the referenceImage viewer, which distorts by one pixel the
            # scaled down pixmap for the reference, hence we'll reuse its size here.
            # target_size = self.selectedViewer.size()
            if not self.bestFit:
                self.scaledReferencePixmap = self.referencePixmap.scaled(
                    target_size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            else:
                self.scaledReferencePixmap = self.referencePixmap.scaled(
                    target_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.referenceViewer.setImage(self.scaledReferencePixmap)
            self.referenceViewer.centerViewAndUpdate()

    @pyqtSlot(float)
    def scaleImagesBy(self, factor):
        """Compute new scale from factor and scale."""
        self.current_scale *= factor
        self.selectedViewer.scaleBy(factor)
        self.referenceViewer.scaleBy(factor)

        self.parent.buttonZoomIn.setEnabled(self.current_scale < 9.0)
        self.parent.buttonZoomOut.setEnabled(self.current_scale > 0.5)
        self.parent.buttonBestFit.setEnabled(self.bestFit is False)
        self.parent.buttonNormalSize.setEnabled(self.current_scale != 1.0)

    @pyqtSlot(float)
    def scaleImagesAt(self, scale):
        """Scale at a pre-computed scale."""
        self.current_scale = scale
        self.selectedViewer.scaleAt(scale)
        self.referenceViewer.scaleAt(scale)

        self.parent.buttonZoomIn.setEnabled(self.current_scale < 9.0)
        self.parent.buttonZoomOut.setEnabled(self.current_scale > 0.5)
        self.parent.buttonBestFit.setEnabled(self.bestFit is False)
        self.parent.buttonNormalSize.setEnabled(self.current_scale != 1.0)

    def resetState(self):
        self.selectedPixmap = QPixmap()
        self.scaledSelectedPixmap = QPixmap()
        self.referencePixmap = QPixmap()
        self.scaledReferencePixmap = QPixmap()
        self.setBestFit(True)
        self.current_scale = 1.0
        self.selectedViewer.resetCenter()
        self.referenceViewer.resetCenter()

        self.parent.buttonZoomIn.setEnabled(False)
        self.parent.buttonZoomOut.setEnabled(False)
        self.parent.buttonBestFit.setEnabled(False) # active mode by default
        self.parent.buttonNormalSize.setEnabled(True)

    def clear_all(self):
        """No item from the model, disable and clear everything."""
        self.resetState()
        self.selectedViewer.setImage(self.selectedPixmap) # null
        self.selectedViewer.setDisabled(True)
        self.referenceViewer.setImage(self.referencePixmap) # null
        self.referenceViewer.setDisabled(True)
        self.parent.buttonImgSwap.setDisabled(True)
        self.parent.buttonNormalSize.setDisabled(True)

    @pyqtSlot()
    def ScaleToBestFit(self):
        """Setup before scaling to bestfit"""
        self.setBestFit(True)
        self.current_scale = 1.0

        self.selectedViewer.scaleAt(1.0)
        self.referenceViewer.scaleAt(1.0)

        self.selectedViewer.resetCenter()
        self.referenceViewer.resetCenter()
        self._updateImages()

        self.parent.buttonBestFit.setEnabled(False)
        self.parent.buttonZoomOut.setEnabled(False)
        self.parent.buttonZoomIn.setEnabled(False)
        self.parent.buttonNormalSize.setEnabled(True)

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

        self.selectedViewer.centerViewAndUpdate()
        self.referenceViewer.centerViewAndUpdate()

        self.selectedViewer.scaleToNormalSize()
        self.referenceViewer.scaleToNormalSize()

        self.parent.buttonNormalSize.setEnabled(False)
        self.parent.buttonZoomIn.setEnabled(True)
        self.parent.buttonZoomOut.setEnabled(True)
        self.parent.buttonBestFit.setEnabled(True)


class QWidgetController(BaseController):
    """Specialized version for QWidget-based viewers."""
    def __init__(self, selectedViewer, referenceViewer, parent):
        super().__init__(selectedViewer, referenceViewer, parent)

    @pyqtSlot(QPointF)
    def onDraggedMouse(self, delta):
        if self.sender() is self.referenceViewer:
            self.selectedViewer.onDraggedMouse(delta)
        else:
            self.referenceViewer.onDraggedMouse(delta)

    @pyqtSlot()
    def swapPixmaps(self):
        self.selectedViewer.getPixmap().swap(self.referenceViewer.getPixmap())
        self.selectedViewer.centerViewAndUpdate()
        self.referenceViewer.centerViewAndUpdate()


class ScrollAreaController(BaseController):
    """Specialized version fro QLabel-based viewers."""
    def __init__(self, selectedViewer, referenceViewer, parent):
        super().__init__(selectedViewer, referenceViewer, parent)

    def _setupConnections(self):
        super()._setupConnections()
        self.selectedViewer.connectScrollBars()
        self.referenceViewer.connectScrollBars()

    @pyqtSlot(QPoint)
    def onDraggedMouse(self, delta):
        self.selectedViewer.ignore_signal = True
        self.referenceViewer.ignore_signal = True

        self.selectedViewer.onDraggedMouse(delta)
        self.referenceViewer.onDraggedMouse(delta)

        self.selectedViewer.ignore_signal = False
        self.referenceViewer.ignore_signal = False

    @pyqtSlot()
    def swapPixmaps(self):
        self.referenceViewer._pixmap.swap(self.selectedViewer._pixmap)
        self.referenceViewer.setCachedPixmap()
        self.selectedViewer.setCachedPixmap()

    @pyqtSlot()
    def syncCenters(self):
        if self.sender() is self.referenceViewer:
            self.selectedViewer.setCenter(self.referenceViewer.getCenter())
        else:
            self.referenceViewer.setCenter(self.selectedViewer.getCenter())

    @pyqtSlot(float, QPointF)
    def onMouseWheel(self, scale, delta):
        self.scaleImagesAt(scale)
        self.selectedViewer.adjustScrollBarsScaled(delta)
        # Signal will automatically change the other:
        # self.referenceViewer.adjustScrollBarsScaled(delta)

    @pyqtSlot(int)
    def onVScrollBarChanged(self, value):
        if self.sender() is self.referenceViewer:
            self.selectedViewer._verticalScrollBar.setValue(value)
        else:
            self.referenceViewer._verticalScrollBar.setValue(value)

    @pyqtSlot(int)
    def onHScrollBarChanged(self, value):
        if self.sender() is self.referenceViewer:
            if not selectedViewer.ignore_signal:
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
    def ScaleToBestFit(self):
        # Disable scrollbars to avoid GridLayout size rounding "error"
        super().ScaleToBestFit()
        print("toggling scrollbars")
        self.selectedViewer.toggleScrollBars()
        self.referenceViewer.toggleScrollBars()

class GraphicsViewController(BaseController):
    """Specialized version fro QGraphicsView-based viewers."""
    def __init__(self, selectedViewer, referenceViewer, parent):
        super().__init__(selectedViewer, referenceViewer, parent)

    @pyqtSlot()
    def syncCenters(self):
        if self.sender() is self.referenceViewer:
            self.selectedViewer.setCenter(self.referenceViewer.getCenter())
        else:
            self.referenceViewer.setCenter(self.selectedViewer.getCenter())


class QWidgetImageViewer(QWidget):
    """Use a QPixmap, but no scrollbars."""
    mouseDragged = pyqtSignal(QPointF)
    mouseWheeled = pyqtSignal(float)

    def __init__(self, parent, name=""):
        super().__init__(parent)
        self._app = QApplication
        self._pixmap = QPixmap()
        self._rect = QRectF()
        self._lastMouseClickPoint = QPointF()
        self._mousePanningDelta = QPointF()
        self._current_scale = 1.0
        self._drag = False
        self._dragConnection = None
        self._wheelConnection = None
        self._instance_name = name
        self.bestFit = True
        self.controller = None
        self.setMouseTracking(False)

    def __repr__(self):
        return f'{self._instance_name}'

    def getPixmap(self):
        return self._pixmap

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
        painter.scale(self._current_scale, self._current_scale)
        painter.translate(self._mousePanningDelta)
        painter.drawPixmap(self._rect.topLeft(), self._pixmap)

    def resetCenter(self):
        """ Resets origin """
        # Make sure we are not still panning around
        self._mousePanningDelta = QPointF()
        self.scaleBy(1.0)
        self.update()

    def changeEvent(self, event):
        if event.type() == QEvent.EnabledChange:
            # print(f"{self} is now {'enabled' if self.isEnabled() else 'disabled'}")
            if self.isEnabled():
                self.connectMouseSignals()
                return
            self.disconnectMouseSignals()

    def mousePressEvent(self, event):
        if self.bestFit:
            event.ignore()
            return
        if event.button() == Qt.LeftButton:
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
        if self.bestFit:
            event.ignore()
            return

        self._mousePanningDelta += (event.pos() - self._lastMouseClickPoint) \
                                    * 1.0 / self._current_scale
        self._lastMouseClickPoint = event.pos()
        if self._drag:
            self.mouseDragged.emit(self._mousePanningDelta)
            self.update()

    def mouseReleaseEvent(self, event):
        if self.bestFit:
            event.ignore()
            return
        if event.button() == Qt.LeftButton:
            self._drag = False

        self._app.restoreOverrideCursor()
        self.setMouseTracking(False)

    def wheelEvent(self, event):
        if self.bestFit:
            event.ignore()
            return

        if event.angleDelta().y() > 0:
            self.mouseWheeled.emit(1.25) # zoom-in
        else:
            self.mouseWheeled.emit(0.8) # zoom-out

    def setImage(self, pixmap):
        if pixmap.isNull():
            if not self._pixmap.isNull():
                self._pixmap = pixmap
                self.disconnectMouseSignals()
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
        self._current_scale *= factor
        self.update()

    def scaleAt(self, scale):
        self._current_scale = scale
        self.update()

    def sizeHint(self):
        return QSize(400, 400)

    @pyqtSlot()
    def scaleToNormalSize(self):
        """Called when the pixmap is set back to original size."""
        self._current_scale = 1.0
        self.update()

    @pyqtSlot(QPointF)
    def onDraggedMouse(self, delta):
        self._mousePanningDelta = delta
        self.update()
        print(f"{self} received drag signal from {self.sender()}")


class ScalablePixmap(QWidget):
    """Container for a pixmap that scales up very fast"""
    def __init__(self, parent):
        super().__init__(parent)
        self._pixmap = QPixmap()
        self._current_scale = 1.0

    def paintEvent(self, event):
        painter = QPainter(self)
        # painter.translate(self.rect().center())
        # painter.setRenderHint(QPainter.Antialiasing, False)
        # scale the coordinate system:
        painter.scale(self._current_scale, self._current_scale)
        painter.drawPixmap(self.rect().topLeft(), self._pixmap) #same as (0,0, self.pixmap)
        # print(f"ScalableWidget paintEvent scale {self._current_scale}")

    def setPixmap(self, pixmap):
        self._pixmap = pixmap
        # self.update()

    def sizeHint(self):
        return self._pixmap.size() * self._current_scale
        # return self._pixmap.size()

    def minimumSizeHint(self):
        return self.sizeHint()

    # def moveEvent(self, event):
    #     print(f"{self} moved by {event.pos()}")


class ScrollAreaImageViewer(QScrollArea):
    """Version with Qlabel for testing"""
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
        self._current_scale = 1.0
        self._drag = False
        self._dragConnection = None
        self._wheelConnection = None
        self._vBarConnection = None
        self._hBarConnection = None
        self._instance_name = name
        self.wantScrollBars = True
        self.bestFit = True
        self.controller = None
        self.label = ScalablePixmap(self)
        # This is to avoid sending signals twice on scrollbar updates
        self.ignore_signal = False

        self.setBackgroundRole(QPalette.Dark)
        self.setWidgetResizable(False)
        self.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        # self.viewport().setAttribute(Qt.WA_StaticContents)
        self.setAlignment(Qt.AlignCenter)

        self._verticalScrollBar = self.verticalScrollBar()
        self._horizontalScrollBar = self.horizontalScrollBar()

        if self.wantScrollBars:
            self.toggleScrollBars()
        else:
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setWidget(self.label)
        self.setVisible(True)

    def __repr__(self):
        return f'{self._instance_name}'

    def getPixmap(self):
        return self._pixmap

    def toggleScrollBars(self):
        if not self.wantScrollBars:
            return
        # Ensure that it's off on the first run
        if self.horizontalScrollBarPolicy() == Qt.ScrollBarAsNeeded:
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

    def mousePressEvent(self, event):
        if self.bestFit:
            event.ignore()
            return
        if event.button() == Qt.LeftButton:
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
        # self.update()

    def mouseReleaseEvent(self, event):
        if self.bestFit:
            event.ignore()
            return
        if event.button() == Qt.LeftButton:
            self._drag = False
        self._app.restoreOverrideCursor()
        self.setMouseTracking(False)
        super().mouseReleaseEvent(event)

    def wheelEvent(self, event):
        if self.bestFit:
            event.ignore()
            return
        oldScale = self._current_scale
        if event.angleDelta().y() > 0:
            self._current_scale *= 1.25 # zoom-in
        else:
            self._current_scale *= 0.8 # zoom-out
        deltaToPos = (event.position() / oldScale) - (self.label.pos() / oldScale)
        delta = (deltaToPos * self._current_scale) - (deltaToPos * oldScale)
        self.mouseWheeled.emit(self._current_scale, delta)

    def setImage(self, pixmap, cache=True):
        if pixmap.isNull():
            if not self._pixmap.isNull():
                self._pixmap = pixmap
                self.update()
            return
        elif not self.isEnabled():
            self.setEnabled(True)
            self.connectMouseSignals()
        self._pixmap = pixmap
        self.label.setPixmap(pixmap)
        self.label.adjustSize()

    def centerViewAndUpdate(self):
        self._rect = self.label.rect()
        self.label.rect().translate(-self._rect.center())
        self.label._current_scale = self._current_scale
        self.label.update()
        # self.viewport().update()

    def setCachedPixmap(self):
        """In case we have changed the cached pixmap, reset it."""
        self.label.setPixmap(self._pixmap)
        self.label.update()

    def shouldBeActive(self):
        return True if not self.pixmap.isNull() else False

    def scaleBy(self, factor):
        self._current_scale *= factor
        # print(f"scaleBy(factor={factor}) current_scale={self._current_scale}")

        # This kills my computer when scaling up! DO NOT USE!
        # self._pixmap = self._pixmap.scaled(
        #         self._pixmap.size().__mul__(factor),
        #         Qt.KeepAspectRatio, Qt.FastTransformation)

        # pointBeforeScale = QPoint(self.viewport().width() / 2,
        #                         self.viewport().height() / 2)
        pointBeforeScale = self.label.rect().center()
        screenCenter = self.rect().center()

        screenCenter.setX(screenCenter.x() + self.horizontalScrollBar().value())
        screenCenter.setY(screenCenter.y() + self.verticalScrollBar().value())

        # WARNING: factor has to be either 1.25 or 0.8 here!
        self.label.resize(self.label.size().__imul__(factor))
        # self.label.updateGeometry()

        self.label._current_scale = self._current_scale
        self.label.update()
        # Center view on zoom change(?) same as imageLabel->resize(imageLabel->pixmap()->size())
        # self.label.adjustSize()

        # pointAfterScale = QPoint(self.viewport().width() / 2,
        #                         self.viewport().height() / 2)
        pointAfterScale = self.label.rect().center()
        # print(f"label.newsize: {self.label.size()}\npointAfter: {pointAfterScale}")

        offset = pointBeforeScale - pointAfterScale
        newCenter = screenCenter - offset #FIXME need factor here somewhere
        # print(f"offset: {offset} newCenter: {newCenter}\n-----------------")

        # self.centerOn(newCenter)

        # self.adjustScrollBarCentered()

    def scaleAt(self, scale):
        self._current_scale = scale
        self.label.resize(self._pixmap.size().__imul__(scale))
        self.label._current_scale = scale
        self.label.update()
        # self.label.adjustSize()

    def centerOn(self, position):
        # TODO here make widget move without the scrollbars if possible

        self.ensureWidgetVisible(self.label) # moves back to center of label
        # self.ensureVisible(position.x(), position.y())
        # self.scrollContentsBy(position.x(), position.y())

        # hvalue = self.horizontalScrollBar().value()
        # vvalue = self.verticalScrollBar().value()
        # topLeft = self.viewport().rect().topLeft()
        # self.label.move(topLeft.x() - hvalue, topLeft.y() - vvalue)
        # self.label.updateGeometry()

    def adjustScrollBarsFactor(self, factor):
        """After scaling, no mouse position, default to center."""
        # scrollBar.setMaximum(scrollBar.maximum() - scrollBar.minimum() + scrollBar.pageStep())
        self._horizontalScrollBar.setValue(int(factor * self._horizontalScrollBar.value() + \
            ((factor - 1) * self._horizontalScrollBar.pageStep()/2)))
        self._verticalScrollBar.setValue(int(factor * self._verticalScrollBar.value() + \
            ((factor - 1) * self._verticalScrollBar.pageStep()/2)))

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

    def adjustScrollBarCentered(self, scrollBar, factor):
        """Just center in the middle."""
        self._horizontalScrollBar.setValue(
            int(self._horizontalScrollBar.maximum() / 2))
        self._verticalScrollBar.setValue(
            int(self._verticalScrollBar.maximum() / 2))

    def resetCenter(self):
        """ Resets origin """
        self._mousePanningDelta = QPoint()
        # self.label._mousePanningDelta = self._mousePanningDelta
        self._current_scale = 1.0
        # self.scaleBy(1.0)
        # self.label.update() # already called in scaleBy

    def setCenter(self, point):
        self._lastMouseClickPoint = point

    def getCenter(self):
        return self._lastMouseClickPoint

    def sizeHint(self):
        return self._pixmap.rect().size()

    def viewportSizeHint(self):
        return self._pixmap.rect().size()

    @pyqtSlot()
    def scaleToNormalSize(self):
        """Called when the pixmap is set back to original size."""
        self.scaleAt(1.0)
        self.ensureWidgetVisible(self.label) # needed for centering
        # self.label.update()
        self.toggleScrollBars()

    @pyqtSlot(QPoint)
    def onDraggedMouse(self, delta):
        """Update position from mouse delta sent by the other panel."""
        self._mousePanningDelta = delta
        # self.label.move(self.label.pos() + delta)
        # self.label.update()

        #FIXME signal from scrollbars has already synced the values here!
        self.adjustScrollBarsAuto()

        # print(f"{self} onDraggedMouse slot with delta {delta}")

    def changeEvent(self, event):
        if event.type() == QEvent.EnabledChange:
            print(f"{self} is now {'enabled' if self.isEnabled() else 'disabled'}")


from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem

class GraphicsViewViewer(QGraphicsView):
    """Re-Implementation."""
    mouseDragged = pyqtSignal()
    mouseWheeled = pyqtSignal(bool)

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
        self._current_scale = 1.0
        self._drag = False
        self._dragConnection = None
        self._wheelConnection = None
        self._instance_name = name
        self.wantScrollBars = True
        self.bestFit = True
        self.controller = None
        self._centerPoint = QPointF(0.0, 0.0)
        self.centerOn(self._centerPoint)

        # specific to this class
        self._scene = QGraphicsScene()
        self._item = QGraphicsPixmapItem()
        self.setScene(self._scene)
        self._scene.addItem(self._item)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

        if self.wantScrollBars:
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        else:
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        self.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.setViewportUpdateMode (QGraphicsView.FullViewportUpdate)
        self.setMouseTracking(True)

    def connectMouseSignals(self):
        if not self._dragConnection:
            self._dragConnection = self.mouseDragged.connect(
                                        self.controller.syncCenters)
        if not self._wheelConnection:
            self._wheelConnection = self.mouseWheeled.connect(
                                        self.controller.scaleImages)

    def disconnectMouseSignals(self):
        if self._dragConnection:
            self.mouseDragged.disconnect()
            self._dragConnection = None
        if self._wheelConnection:
            self.mouseWheeled.disconnect()
            self._wheelConnection = None

    def mousePressEvent(self, event):
        if self.bestFit:
            event.ignore()
            return
        if event.button() == Qt.LeftButton:
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
        # event.accept()

    def mouseMoveEvent(self, event):
        if self.bestFit:
            event.ignore()
            return

        self._centerPoint = self.mapToScene( self.rect().center() )
        super().mouseMoveEvent(event)

        if self._drag:
            self.mouseDragged.emit()
            # self._item.update()


    def mouseReleaseEvent(self, event):
        if self.bestFit:
            event.ignore()
            return
        if event.button() == Qt.LeftButton:
            self._drag = False

        self._app.restoreOverrideCursor()
        self.setMouseTracking(False)
        super().mouseReleaseEvent(event)

    def wheelEvent(self, event):
        if self.bestFit:
            event.ignore()
            return

        if event.angleDelta().y() > 0:
            self.mouseWheeled.emit(True) # zoom-in
        else:
            self.mouseWheeled.emit(False) # zoom-out


    def setImage(self, pixmap):
        self._pixmap = pixmap
        self._item.setPixmap(pixmap)
        # offset = -QRectF(pixmap.rect()).center()
        # self._item.setOffset(offset)
        # self.setSceneRect(offset.x()*4, offset.y()*4, -offset.x()*8, -offset.y()*8)
        self.translate(1, 1)
        # self._scene.setSceneRect(self._pixmap.rect())

    def centerViewAndUpdate(self):
        pass

    def scaleBy(self, factor):
        # super().scale(factor, factor)
        self.zoom(factor)

    def setCenter(self, point):
        self._centerPoint = point
        self.centerOn(self._centerPoint)

    def getCenter(self):
        return self._centerPoint

    def resetCenter(self):
        """ Resets origin """
        self._mousePanningDelta = QPointF()
        self._current_scale = 1.0
        self.scaleBy(1.0)
        # self.update()
        self.setCenter(self._scene.sceneRect().center())

    def setNewCenter(self, position):
        self._centerPoint = position
        self.centerOn(self._centerPoint)

    @pyqtSlot()
    def scaleToNormalSize(self):
        """Called when the pixmap is set back to original size."""
        self.scaleBy(1.0) # FIXME

        super().fitInView(self._scene.sceneRect(), Qt.KeepAspectRatio )
        self.setNewCenter(self._scene.sceneRect().center())
        self.update()

    # def sizeHint(self):
    #     return self._item.rect().size()

    # def viewportSizeHint(self):
    #     return self._item.rect().size()

    def zoom_in(self):
        self.zoom(self._scaleFactor)

    def zoom_out(self):
        self.zoom(1.0 / self._scaleFactor)

    def zoom(self, factor):
        #Get the position of the mouse before scaling, in scene coords
        pointBeforeScale = QPointF(self.mapToScene(self.mapFromGlobal(QCursor.pos())))

        #Get the original screen centerpoint
        screenCenter = self.mapToScene( self.rect().center() )

        super().scale(factor, factor)

        #Get the position after scaling, in scene coords
        pointAfterScale = QPointF( self.mapToScene( self.mapFromGlobal(QCursor.pos()) ) )

        #Get the offset of how the screen moved
        offset = QPointF( pointBeforeScale - pointAfterScale)

        #Adjust to the new center for correct zooming
        newCenter = QPointF(screenCenter + offset)
        self.setNewCenter(newCenter)

        # self.updateSceneRect(self._item.rect()) # TEST THIS?

        # mouse position has changed!!
        # emit mouseMoved( QGraphicsView::mapToScene( event->pos() ) );
        # emit mouseMoved( QGraphicsView::mapToScene( mapFromGlobal(QCursor::pos()) ) );
        # emit somethingChanged();

