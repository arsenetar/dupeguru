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
    """Base proxy interface to keep image viewers synchronized.
    Relays function calls. Singleton. """

    def __init__(self, selectedViewer, referenceViewer, parent):
        super().__init__()
        self.selectedViewer = selectedViewer
        self.referenceViewer = referenceViewer

        # cached pixmaps
        self.selectedPixmap = QPixmap()
        self.referencePixmap = QPixmap()
        self.scaledSelectedPixmap = QPixmap()
        self.scaledReferencePixmap = QPixmap()

        self.current_scale = 1.0
        self._scaleFactor = 1.3 # how fast we zoom
        self.bestFit = True
        self.wantScrollBars = True
        self.parent = parent #needed to change buttons' states
        self.selectedViewer.controller = self
        self.referenceViewer.controller = self
        self._setupConnections()

    def _setupConnections(self):
        self.selectedViewer.connect_signals()
        self.referenceViewer.connect_signals()

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
            self.selectedViewer.center_and_update()

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
            self.referenceViewer.center_and_update()

    def zoom_in(self):
        self.scaleImages(True)

    def zoom_out(self):
        self.scaleImages(False)

    @pyqtSlot(bool) # True = zoom-in
    def scaleImages(self, zoom_type):

        if zoom_type: # zoom_in
            self.current_scale *= self._scaleFactor
            self.selectedViewer.zoom_in()
            self.referenceViewer.zoom_in()
        else:
            self.current_scale /= self._scaleFactor
            self.selectedViewer.zoom_out()
            self.referenceViewer.zoom_out()

        # self.selectedViewer.scaleBy(self.scaleFactor)
        # self.referenceViewer.scaleBy(self.scaleFactor)

        self.parent.buttonZoomIn.setEnabled(self.current_scale < 16.0)
        self.parent.buttonZoomOut.setEnabled(self.current_scale > 1.0)
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
    def scale_to_bestfit(self):
        """Setup before scaling to bestfit"""
        self.setBestFit(True)
        self.current_scale = 1.0

        self.selectedViewer.scaleBy(1.0)
        self.referenceViewer.scaleBy(1.0)

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

        self.selectedViewer.center_and_update()
        self.referenceViewer.center_and_update()

        self.selectedViewer.pixmapReset()
        self.referenceViewer.pixmapReset()

        self.parent.buttonNormalSize.setEnabled(False)
        self.parent.buttonZoomIn.setEnabled(True)
        self.parent.buttonZoomOut.setEnabled(True)
        self.parent.buttonBestFit.setEnabled(True)

    def syncCenters(self): # virtual
        pass

    def swapPixmaps(self): #virtual
        pass



class QWidgetController(BaseController):
    """Specialized version for QWidget-based viewers"""
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
        self.selectedViewer.center_and_update()
        self.referenceViewer.center_and_update()




class ScrollAreaController(BaseController):
    """Specialized version fro QLabel-based viewers"""
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
        self.referenceViewer._pixmap.swap(self.selectedViewer._pixmap)
        self.referenceViewer.setCachedPixmap()
        self.selectedViewer.setCachedPixmap()

    @pyqtSlot()
    def syncCenters(self):
        self.selectedViewer.setCenter(self.referenceViewer.getCenter())
        self.referenceViewer.setCenter(self.selectedViewer.getCenter())



class GraphicsViewController(BaseController):
    """Specialized version fro QGraphicsView-based viewers"""
    def __init__(self, selectedViewer, referenceViewer, parent):
        super().__init__(selectedViewer, referenceViewer, parent)

    @pyqtSlot(QPointF)
    def onDraggedMouse(self, delta):
        if self.sender() is self.referenceViewer:
            self.selectedViewer.onDraggedMouse(delta)
        else:
            self.referenceViewer.onDraggedMouse(delta)

    @pyqtSlot()
    def syncCenters(self):
        self.selectedViewer.setCenter(self.referenceViewer.getCenter())
        self.referenceViewer.setCenter(self.selectedViewer.getCenter())


class QWidgetImageViewer(QWidget):
    """Uses a QPixmap as the center piece."""
    mouseDragged = pyqtSignal(QPointF)
    mouseWheeled = pyqtSignal(bool)

    def __init__(self, parent, name=""):
        super().__init__(parent)
        self._app = QApplication
        self._pixmap = QPixmap()
        self._rect = QRectF()
        self._reference = QPointF()
        self._delta = QPointF()
        self._scaleFactor = 1.3
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

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.translate(self.rect().center())
        painter.scale(self._current_scale, self._current_scale)
        painter.translate(self._delta)
        painter.drawPixmap(self._rect.topLeft(), self._pixmap)
        # print(f"{self} paintEvent delta={self._delta} current scale={self._current_scale}")

    def resetCenter(self):
        """ Resets origin """
        self._delta = QPointF() # FIXME does this even work?
        self.scaleBy(1.0)
        self.update()

    def changeEvent(self, event):
        if event.type() == QEvent.EnabledChange:
            print(f"{self} is now {'enabled' if self.isEnabled() else 'disabled'}")
            if self.isEnabled():
                self.connect_signals()
                return
            self.disconnect_signals()

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

        self._reference = event.pos()
        self._app.setOverrideCursor(Qt.ClosedHandCursor)
        self.setMouseTracking(True)
        event.accept()

    def mouseMoveEvent(self, event):
        if self.bestFit:
            event.ignore()
            return

        self._delta += (event.pos() - self._reference) * 1.0 / self._current_scale
        self._reference = event.pos()
        if self._drag:
            self.mouseDragged.emit(self._delta)
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
            self.mouseWheeled.emit(True) # zoom-in
        else:
            self.mouseWheeled.emit(False) # zoom-out

    def setImage(self, pixmap):
        if pixmap.isNull():
            if not self._pixmap.isNull():
                self._pixmap = pixmap
                self.disconnect_signals()
                self.update()
            return
        elif not self.isEnabled():
            self.setEnabled(True)
            self.connect_signals()
        self._pixmap = pixmap

    def center_and_update(self):
        self._rect = self._pixmap.rect()
        self._rect.translate(-self._rect.center())
        self.update()

    def shouldBeActive(self):
        return True if not self.pixmap.isNull() else False

    def connect_signals(self):
        if not self._dragConnection:
            self._dragConnection = self.mouseDragged.connect(
                                        self.controller.onDraggedMouse)
        if not self._wheelConnection:
            self._wheelConnection = self.mouseWheeled.connect(
                                        self.controller.scaleImages)

    def disconnect_signals(self):
        if self._dragConnection:
            self.mouseDragged.disconnect()
            self._dragConnection = None
        if self._wheelConnection:
            self.mouseWheeled.disconnect()
            self._wheelConnection = None

    def zoom_in(self):
        self._current_scale *= 1.25
        self.update()

    def zoom_out(self):
        self._current_scale *= 0.8
        self.update()

    def scaleBy(self, factor):
        self._current_scale = factor
        self.update()

    def sizeHint(self):
        return QSize(400, 400)

    @pyqtSlot()
    def pixmapReset(self):
        """Called when the pixmap is set back to original size."""
        self._current_scale = 1.0
        self.update()

    @pyqtSlot(QPointF)
    def onDraggedMouse(self, delta):
        self._delta = delta
        self.update()
        print(f"{self} received drag signal from {self.sender()}")



class QLabelNoAA(QLabel):
    def __init__(self, parent):
        super().__init__(parent)
        self._pixmap = QPixmap()
        self._current_scale = 1.0
        self._scaleFactor = 1.3
        self._delta = QPointF()
        self._rect = QRectF()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.translate(self.rect().center())
        # painter.setRenderHint(QPainter.Antialiasing, False)
        # scale the coordinate system:
        painter.scale(self._current_scale, self._current_scale)
        painter.translate(self._delta)
        painter.drawPixmap(self.rect().topLeft(), self._pixmap)
        print(f"LabelnoAA paintEvent scale {self._current_scale}")

    def setPixmap(self, pixmap):
        self._pixmap = pixmap
        # self.center_and_update()
        super().setPixmap(pixmap)

    # def center_and_update(self):
    #     self._rect = self.rect()
    #     self._rect.translate(-self._rect.center())
    #     self._update(self._current_scale)

    def sizeHint(self):
        return self._pixmap.size() * self._current_scale


class ScalableWidget(QWidget):
    def __init__(self, parent):
        super().__init__()
        self._pixmap = QPixmap()
        self._current_scale = 1.0
        self._scaleFactor = 1.3
        self._delta = QPointF()
        self._rect = QRectF()

    def paintEvent(self, event):
        painter = QPainter(self)
        # painter.translate(self.rect().center())
        # painter.setRenderHint(QPainter.Antialiasing, False)
        # scale the coordinate system:
        painter.scale(self._current_scale, self._current_scale)
        painter.translate(self._delta)
        painter.drawPixmap(self.rect().topLeft(), self._pixmap)
        print(f"ScalableWidget paintEvent scale {self._current_scale}")

    def setPixmap(self, pixmap):
        self._pixmap = pixmap
        # self.center_and_update()
        # super().setPixmap(pixmap)

    # def center_and_update(self):
    #     self._rect = self.rect()
    #     self._rect.translate(-self._rect.center())
    #     self._update(self._current_scale)

    def sizeHint(self):
        # if self._current_scale <= 1.0:
        #     return self._pixmap.size()
        return self._pixmap.size() * self._current_scale


class ScrollAreaImageViewer(QScrollArea):
    """Version with Qlabel for testing"""
    mouseDragged = pyqtSignal(QPointF)
    mouseWheeled = pyqtSignal(bool)

    def __init__(self, parent, name=""):
        super().__init__(parent)
        self._parent = parent
        self._app = QApplication
        self._pixmap = QPixmap()
        self._scaledpixmap = None
        self._rect = QRectF()
        self._reference = QPointF()
        self._delta = QPointF()
        self._scaleFactor = 1.3
        self._current_scale = 1.0
        self._drag = False
        self._dragConnection = None
        self._wheelConnection = None
        self._instance_name = name
        self.wantScrollBars = True
        self.bestFit = True
        self.controller = None

        self.label = ScalableWidget(self)

        if isinstance(self.label, QLabelNoAA):
            sizePolicy = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
            self.label.setBackgroundRole(QPalette.Base)
            self.label.setSizePolicy(sizePolicy)
            # self.label.setAlignment(Qt.AlignCenter) # useless?
            self.label.setScaledContents(True) # Available in QLabel only, not used
            # self.label.adjustSize()

        self.setBackgroundRole(QPalette.Dark)
        self.setWidgetResizable(False)
        self.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        # self.viewport().setAttribute(Qt.WA_StaticContents)
        self.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        if self.wantScrollBars:
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        else:
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setWidget(self.label)
        self.setVisible(True)

        if self.wantScrollBars:
            self._verticalScrollBar = self.verticalScrollBar()
            self._horizontalScrollBar = self.horizontalScrollBar()

            self._verticalScrollBar.rangeChanged.connect(
                self.printvalue)
            self._horizontalScrollBar.rangeChanged.connect(
                self.printvalue)

    @pyqtSlot()
    def printvalue(self):
        print(f"verticalscrollbar.maximum: {self._verticalScrollBar.maximum()}")

    def __repr__(self):
        return f'{self._instance_name}'

    def getPixmap(self):
        return self._pixmap

    def connect_signals(self):
        if not self._dragConnection:
            self._dragConnection = self.mouseDragged.connect(
                                        self.controller.onDraggedMouse)
        if not self._wheelConnection:
            self._wheelConnection = self.mouseWheeled.connect(
                                        self.controller.scaleImages)

    def disconnect_signals(self):
        if self._dragConnection:
            self.mouseDragged.disconnect()
            self._dragConnection = None
        if self._wheelConnection:
            self.mouseWheeled.disconnect()
            self._wheelConnection = None

    def changeEvent(self, event):
        if event.type() == QEvent.EnabledChange:
            print(f"{self} is now {'enabled' if self.isEnabled() else 'disabled'}")

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

        self._reference = event.pos()
        self._app.setOverrideCursor(Qt.ClosedHandCursor)
        self.setMouseTracking(True)
        event.accept()

    def mouseMoveEvent(self, event):
        if self.bestFit:
            event.ignore()
            return

        self._delta += (event.pos() - self._reference) * 1.0/self._current_scale
        self._reference = event.pos()
        if self._drag:
            self.mouseDragged.emit(self._delta)
            self.label._delta = self._delta
            self.label.update()

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
            self.mouseWheeled.emit(True) # zoom-in
        else:
            self.mouseWheeled.emit(False) # zoom-out

    def setImage(self, pixmap, cache=True):
        if pixmap.isNull():
            if not self._pixmap.isNull():
                self._pixmap = pixmap
                self.update()
            return
        elif not self.isEnabled():
            self.setEnabled(True)
            self.connect_signals()

        self._pixmap = pixmap
        self.label.setPixmap(pixmap)
        self.label.adjustSize()

    def center_and_update(self):
        self._rect = self.rect()
        self._rect.translate(-self._rect.center())
        self.label._current_scale = self._current_scale
        self.label.update()
        # self.viewport().update()

    def setCachedPixmap(self):
        """In case we have changed the cached pixmap, reset it."""
        self.label.setPixmap(self._pixmap)
        self.label.update()

    def shouldBeActive(self):
        return True if not self.pixmap.isNull() else False

    def zoom_in(self):
        self._current_scale *= 1.25
        self.scaleBy(self._current_scale)

    def zoom_out(self):
        self._current_scale *= 0.8
        self.scaleBy(self._current_scale)

    def scaleBy(self, factor):
        print(f"{self} current_scale={self._current_scale}")
        # This kills my computer when scaling up! DO NOT USE!
        # self._pixmap = self._pixmap.scaled(
        #         self._pixmap.size().__mul__(factor),
        #         Qt.KeepAspectRatio, Qt.FastTransformation)

        # self.label.setPixmap(self._pixmap)

        # This does nothing:
        # newsize = self._pixmap.size().__imul__(factor)
        # self.label.resize(newsize)
        if self._current_scale < 1.0:
            self.label.resize(self._pixmap.size())




        # we might need a QRect here to update?
        self.label._current_scale = factor
        self.label.update()



        self.label.adjustSize() # needed to center view on zoom change

        if self.wantScrollBars:
            self.adjustScrollBar(self.horizontalScrollBar(), factor)
            self.adjustScrollBar(self.verticalScrollBar(), factor)


    def adjustScrollBar(self, scrollBar, factor):
        # scrollBar.setMaximum(
        #     scrollBar.maximum() - scrollBar.minimum() + scrollBar.pageStep())
        # scrollBar.setValue(int(
        #     factor * scrollBar.value() +
        #     ((factor - 1) * scrollBar.pageStep()/2)))
        scrollBar.setValue(int(scrollBar.maximum() / 2))

        # self.viewport().update()

    def resetCenter(self):
        """ Resets origin """
        self._delta = QPointF()
        self.label._delta = self._delta
        self._current_scale = 1.0
        self.scaleBy(1.0)
        # self.label.update() # already called in scaleBy

    def setCenter(self, point):
        self._reference = point

    def getCenter(self):
        return self._reference

    def sizeHint(self):
        return self._pixmap.rect().size()

    def viewportSizeHint(self):
        return self._pixmap.rect().size()

    @pyqtSlot()
    def pixmapReset(self):
        """Called when the pixmap is set back to original size."""
        self._current_scale = 1.0
        self.scaleBy(1.0)
        # self.ensureWidgetVisible(self.label) # might not need
        self.label.update()

    @pyqtSlot(QPointF)
    def onDraggedMouse(self, delta):
        # This updates position from mouse delta from other panel
        self._delta = delta
        self.label._delta = delta
        self.label.update()
        print(f"{self} received mouse drag signal from {self.sender()}")




from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem

class GraphicsViewViewer(QGraphicsView):
    """Re-Implementation."""
    mouseDragged = pyqtSignal(QPointF)
    mouseWheeled = pyqtSignal(bool)

    def __init__(self, parent, name=""):
        super().__init__(parent)
        self._parent = parent
        self._app = QApplication
        self._pixmap = QPixmap()
        self._scaledpixmap = None
        self._rect = QRectF()
        self._reference = QPointF()
        self._delta = QPointF()
        self._scaleFactor = 1.3
        self._current_scale = 1.0
        self._drag = False
        self._dragConnection = None
        self._wheelConnection = None
        self._instance_name = name
        self.wantScrollBars = True
        self.bestFit = True
        self.controller = None
        self._centerPoint = QPointF()

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
        # self.setViewportUpdateMode (QGraphicsView.FullViewportUpdate)

    def connect_signals(self):
        if not self._dragConnection:
            self._dragConnection = self.mouseDragged.connect(
                                        self.controller.onDraggedMouse)
        if not self._wheelConnection:
            self._wheelConnection = self.mouseWheeled.connect(
                                        self.controller.scaleImages)

    def disconnect_signals(self):
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

        self._reference = event.pos()
        self._app.setOverrideCursor(Qt.ClosedHandCursor)
        self.setMouseTracking(True)
        event.accept()

    def mouseMoveEvent(self, event):
        if self.bestFit:
            event.ignore()
            return

        self._delta += (event.pos() - self._reference) * 1.0/self._current_scale
        self._reference = event.pos()
        if self._drag:
            self.mouseDragged.emit(self._delta)
            self.label.update()
            super().mouseMoveEvent(event)

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
        self._scene.setSceneRect(self._pixmap.rect())

    def scaleBy(self, factor):
        # super().scale(factor, factor)
        self.zoom(factor)

    def resetCenter(self):
    #     """ Resets origin """
    #     self._delta = QPointF()
    #     self._scaleFactor = 1.0
    #     self.scale(self._scaleFactor)
    #     self.update()
        pass

    def setNewCenter(self, position):
        self._centerPoint = position
        self.centerOn(self._centerPoint)

    @pyqtSlot()
    def pixmapReset(self):
        """Called when the pixmap is set back to original size."""
        self.scaleBy(1.0)

        super().fitInView(self._scene.sceneRect(), Qt.KeepAspectRatio )
        self.setNewCenter(self._scene.sceneRect().center())
        self.update()

    @pyqtSlot(QPointF)
    def onDraggedMouse(self, delta):
        self._delta = delta
        # self._item.move()
        print(f"{self} received mouse drag signal from {self.sender()}")

    def sizeHint(self):
        return self._item.rect().size()

    def viewportSizeHint(self):
        return self._item.rect().size()

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

