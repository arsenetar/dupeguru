# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from PyQt5.QtCore import QObject, Qt, QSize, QRectF, QPointF, pyqtSlot, pyqtSignal, QEvent
from PyQt5.QtGui import QPixmap, QPainter, QPalette
from PyQt5.QtWidgets import ( QLabel, QSizePolicy, QWidget, QScrollArea,
                              QScrollBar, QApplication, QAbstractScrollArea )

#TODO: fix panning while zoomed-in
#TODO: fix scroll area not showing up
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

        self.scaleFactor = 1.0
        self.bestFit = True
        self.parent = parent #needed to change buttons' states
        self.selectedViewer.controller = self
        self.referenceViewer.controller = self
        self._setupConnections()

    def _setupConnections(self): #virtual
        pass

    def update(self, ref, dupe):
        self.resetState()
        self.selectedPixmap = QPixmap(str(dupe.path))
        if ref is dupe: # currently selected file is the actual reference file
            self.referencePixmap = QPixmap()
            self.scaledReferencePixmap = QPixmap()
            self.parent.buttonImgSwap.setEnabled(False)
            # disable the blank widget.
            self.referenceViewer.setPixmap(self.referencePixmap)
        else:
            self.referencePixmap = QPixmap(str(ref.path))
            self.parent.buttonImgSwap.setEnabled(True)
            # self.enable_widget(self.referenceViewer)

        # self.update_selected_widget()
        # self.update_reference_widget()

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
            self.selectedViewer.setPixmap(self.scaledSelectedPixmap)

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
            self.referenceViewer.setPixmap(self.scaledReferencePixmap)

    @pyqtSlot(float)
    def scaleImages(self, factor):
        self.scaleFactor *= factor
        print(f'Controller scaleFactor = \
            {self.scaleFactor} (+factor {factor})')

        self.parent.buttonZoomIn.setEnabled(self.scaleFactor < 16.0)
        self.parent.buttonZoomOut.setEnabled(self.scaleFactor > 1.0)
        self.parent.buttonBestFit.setEnabled(self.bestFit is False)
        self.parent.buttonNormalSize.setEnabled(self.scaleFactor != 1.0)

    def sefCenter(self):
        #FIXME need specialization?
        self.selectedViewer.setCenter()
        self.referenceViewer.setCenter()

    def resetState(self):
        self.selectedPixmap = QPixmap()
        self.scaledSelectedPixmap = QPixmap()
        self.referencePixmap = QPixmap()
        self.scaledReferencePixmap = QPixmap()

        self.setBestFit(True)
        self.scaleFactor = 1.0
        self.setCenter()

        self.parent.buttonZoomIn.setEnabled(False)
        self.parent.buttonZoomOut.setEnabled(False)
        self.parent.buttonBestFit.setEnabled(False) # active mode by default
        self.parent.buttonNormalSize.setEnabled(True)

    def clear_all(self):
        """No item from the model, disable and clear everything."""
        self.resetState()
        self.selectedViewer.setPixmap(QPixmap())
        self.selectedViewer.setDisabled(True)
        self.referenceViewer.setPixmap(QPixmap())
        self.referenceViewer.setDisabled(True)

        self.parent.buttonImgSwap.setDisabled(True)
        self.parent.buttonNormalSize.setDisabled(True)

    @pyqtSlot()
    def swapPixmaps(self):
        self.selectedViewer.getPixmap().swap(self.referenceViewer.getPixmap())
        self.selectedViewer.center_and_update()
        self.referenceViewer.center_and_update()

    @pyqtSlot()
    def zoomBestFit(self):
        self.setBestFit(True)
        self.scaleFactor = 1.0
        self.parent.buttonBestFit.setEnabled(False)
        self.parent.buttonZoomOut.setEnabled(False)
        self.parent.buttonZoomIn.setEnabled(False)
        self.parent.buttonNormalSize.setEnabled(True)

    @pyqtSlot()
    def zoomNormalSize(self):
        self.setBestFit(False)
        self.scaleFactor = 1.0

        self.selectedViewer.setPixmap(self.selectedPixmap)
        self.referenceViewer.setPixmap(self.referencePixmap)

        # self.update_selected_widget()
        # self.update_reference_widget()

        self.selectedViewer.pixmapReset()
        self.referenceViewer.pixmapReset()

        self.parent.buttonNormalSize.setEnabled(False)
        self.parent.buttonZoomIn.setEnabled(True)
        self.parent.buttonZoomOut.setEnabled(True)
        self.parent.buttonBestFit.setEnabled(True)

    def setBestFit(self, value):
        self.bestFit = value
        self.selectedViewer.bestFit = value
        self.referenceViewer.bestFit = value

    def setCenter(self):
        self.selectedViewer.setCenter()
        self.referenceViewer.setCenter()


    # def update_selected_widget(self):
    #     print("update_selected_widget()")
    #     if not self.selectedPixmap.isNull():
    #         self.enable_widget(self.selectedViewer)
    #         self.connect_signal(self.selectedViewer, self.referenceViewer)
    #     else:
    #         self.disable_widget(self.selectedViewer)
    #         self.disconnect_signal(self.referenceViewer)

    # def update_reference_widget(self):
    #     print("update_reference_widget()")
    #     if not self.referencePixmap.isNull():
    #         self.enable_widget(self.referenceViewer)
    #         self.connect_signal(self.referenceViewer, self.selectedViewer)
    #     else:
    #         self.disable_widget(self.referenceViewer)
    #         self.disconnect_signal(self.selectedViewer)

    # def enable_widget(self, widget):
    #     if not widget.isEnabled():
    #         widget.setEnabled(True)

    # def disable_widget(self, widget):
    #     """Disables this widget and prevents receiving signals from other_widget."""
    #     print(f"disable_widget({widget})")
    #     widget.setPixmap(QPixmap())
    #     widget.setDisabled(True)

    # def connect_signal(self, widget, other_widget):
    #     """We want this widget to send its signal to the other_widget."""
    #     print(f"connect_signal({widget}, {other_widget})")
    #     if widget.connection is None:
    #         if other_widget.isEnabled():
    #             widget.connection = widget.mouseDragged.connect(other_widget.slot_paint_event)
    #             print(f"Connected signal from {widget} to slot of {other_widget}")

    # def disconnect_signal(self, other_widget):
    #     """We don't want this widget to send its signal anymore to the other_widget."""
    #     print(f"disconnect_signal({other_widget}")
    #     if other_widget.connection:
    #         other_widget.mouseDragged.disconnect()
    #         other_widget.connection = None
    #         print(f"Disconnected signal from {other_widget}")



class QWidgetImageViewerController(BaseController):
    """Specialized version for QWidget-based viewers"""
    def __init__(self, selectedViewer, referenceViewer, parent):
        super().__init__(selectedViewer, referenceViewer, parent)
        # self._setupConnections()

    def _setupConnections(self):
        # self.selectedViewer._wheelConnection = \
        #     self.selectedViewer.mouseWheeled.connect(self.scaleImages)
        # self.referenceViewer._wheelConnection = \
        #     self.referenceViewer.mouseWheeled.connect(self.scaleImages)
        self.selectedViewer.connect_signals()
        self.referenceViewer.connect_signals()

    def scale(self, factor):
        self.selectedViewer.scale(factor)
        self.referenceViewer.scale(factor)

    @pyqtSlot(float)
    def scaleImages(self, factor):
        super().scaleImages(factor)
        # we scale the Qwidget itself in this case
        self.selectedViewer.scale(self.scaleFactor)
        self.referenceViewer.scale(self.scaleFactor)

    def scale_to_bestfit(self):
        self.scale(1.0)
        super().setCenter()
        super()._updateImages()

    @pyqtSlot(QPointF)
    def slot_paint_event(self, delta):
        if self.sender() is self.referenceViewer:
            self.selectedViewer.slot_paint_event(delta)
        else:
            self.referenceViewer.slot_paint_event(delta)



class QLabelImageViewerController(BaseController):
    """Specialized version fro QLabel-based viewers"""
    def __init__(self, selectedViewer, referenceViewer, parent):
        super().__init__(selectedViewer, referenceViewer, parent)

    def scale(self, factor):
        pass #FIXME

    @pyqtSlot(float)
    def scaleImages(self, factor):
        super().scaleImages(factor)
        # we scale the member Qlable in this case
        self.selectedViewer.scale(self.scaleFactor)
        self.referenceViewer.scale(self.scaleFactor)

class GraphicsViewController(BaseController):
    """Specialized version fro QGraphicsView-based viewers"""
    #TODO
    pass


class QWidgetImageViewer(QWidget):
    """Displays image and allows manipulations."""
    mouseDragged = pyqtSignal(QPointF)
    mouseWheeled = pyqtSignal(float)

    def __init__(self, parent, name=""):
        super().__init__(parent)
        self._app = QApplication
        self._pixmap = QPixmap()
        self._rect = QRectF()
        self._reference = QPointF()
        self._delta = QPointF()
        self._scaleFactor = 1.0
        self._drag = False
        self._dragConnection = None
        self._wheelConnection = None
        self._instance_name = name
        self.bestFit = True
        self.controller = None

    def __repr__(self):
        return f'{self._instance_name}'

    def getPixmap(self):
        return self._pixmap

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.translate(self.rect().center())
        painter.scale(self._scaleFactor, self._scaleFactor)
        painter.translate(self._delta)
        painter.drawPixmap(self._rect.topLeft(), self._pixmap)
        # print(f"{self} paintEvent delta={self._delta}")

    def setCenter(self):
        """ Resets origin """
        self._delta = QPointF()
        self._scaleFactor = 1.0
        self.scale(self._scaleFactor)
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
        if event.buttons() == Qt.LeftButton:
            self._drag = True

        self._reference = event.pos()
        self._app.setOverrideCursor(Qt.ClosedHandCursor)
        self.setMouseTracking(True)

    def mouseMoveEvent(self, event):
        if self.bestFit:
            event.ignore()
            return

        self._delta += (event.pos() - self._reference) * 1.0/self._scaleFactor
        self._reference = event.pos()
        if self._drag:
            self.mouseDragged.emit(self._delta)
        self.update()

    def mouseReleaseEvent(self, event):
        if self.bestFit:
            event.ignore()
            return
        if event.buttons() == Qt.LeftButton:
            drag = False

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

    def setPixmap(self, pixmap):
        if pixmap.isNull():
            if not self._pixmap.isNull():
                self._pixmap = pixmap
                self.disconnect_signals()
                self.update()
            return
        elif not self.isEnabled():
            self.connect_signals()
            self.setEnabled(True)
        self._pixmap = pixmap
        self.center_and_update()

    def center_and_update(self):
        self._rect = self._pixmap.rect()
        self._rect.translate(-self._rect.center())
        self.update()

    def isActive(self):
        return True if not self.pixmap.isNull() else False

    def disconnect_signals(self):
        if self._dragConnection:
            self.mouseDragged.disconnect()
            self._dragConnection = None
        if self._wheelConnection:
            self.mouseWheeled.disconnect()
            self._wheelConnection = None

    def connect_signals(self):
        if not self._dragConnection:
            self._dragConnection = self.mouseDragged.connect(
                                        self.controller.slot_paint_event)
        if not self._wheelConnection:
            self._wheelConnection = self.mouseWheeled.connect(
                                        self.controller.scaleImages)

    def scale(self, factor):
        self._scaleFactor = factor
        self.update()

    def sizeHint(self):
        return QSize(400, 400)

    @pyqtSlot()
    def pixmapReset(self):
        """Called when the pixmap is set back to original size."""
        self._scaleFactor = 1.0
        self.update()

    @pyqtSlot(QPointF)
    def slot_paint_event(self, delta):
        self._delta = delta
        self.update()
        # print(f"{self} received drag signal from {self.sender()}")


class ScrollAreaImageViewer(QScrollArea):
    """Version with Qlabel for testing"""
    mouseDragged = pyqtSignal(QPointF)

    def __init__(self, parent, name=""):
        super().__init__(parent)
        self._parent = parent
        self._app = QApplication
        self._pixmap = QPixmap()
        self._rect = QRectF()
        self._reference = QPointF()
        self._delta = QPointF()
        self._scaleFactor = 1.0
        self._drag = False
        self.connection = None # signal bound to a slot
        self._instance_name = name
        self.controller = None

        self.label = QLabel()
        sizePolicy = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setBackgroundRole(QPalette.Base)
        self.label.setSizePolicy(sizePolicy)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setScaledContents(True)

        self.scrollarea = QScrollArea(self)
        self.setBackgroundRole(QPalette.Dark)
        self.setWidgetResizable(True)
        self.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        # self.scrollarea.viewport().setAttribute(Qt.WA_StaticContents)

        self.setWidget(self.label)
        self.setVisible(True)

    def __repr__(self):
        return f'{self._instance_name}'

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.translate(self.rect().center())
        painter.scale(self._scaleFactor, self._scaleFactor)
        painter.translate(self._delta)
        painter.drawPixmap(self._rect.topLeft(), self._pixmap)
        # print(f"{self} paintEvent delta={self._delta}")

    def setCenter(self):
        """ Resets origin """
        self._delta = QPointF()
        self._scaleFactor = 1.0
        self.scale(self._scaleFactor)
        self.update()

    def changeEvent(self, event):
        if event.type() == QEvent.EnabledChange:
            print(f"{self} is now {'enabled' if self.isEnabled() else 'disabled'}")

    def mousePressEvent(self, event):
        if self._parent.bestFit:
            event.ignore()
            return
        if event.buttons() == Qt.LeftButton:
            self._drag = True

        self._reference = event.pos()
        self._app.setOverrideCursor(Qt.ClosedHandCursor)
        self.setMouseTracking(True)

    def mouseMoveEvent(self, event):
        if self._parent.bestFit:
            event.ignore()
            return

        self._delta += (event.pos() - self._reference) * 1.0/self._scaleFactor
        self._reference = event.pos()
        if self._drag:
            self.mouseDragged.emit(self._delta)
        self.update()

    def mouseReleaseEvent(self, event):
        if self._parent.bestFit:
            event.ignore()
            return
        if event.buttons() == Qt.LeftButton:
            drag = False

        self._app.restoreOverrideCursor()
        self.setMouseTracking(False)

    def wheelEvent(self, event):
        if self._parent.bestFit:
            event.ignore()
            return

        if event.angleDelta().y() > 0:
            self._parent.zoomIn()
        else:
            self._parent.zoomOut()

    def setPixmap(self, pixmap):
        #FIXME refactored
        # if pixmap.isNull():
        #     if not self._pixmap.isNull():
        #         self._pixmap = pixmap
        #         self.update()
        #     return
        # elif not self.isEnabled():
        #     self.setEnabled(True)
        # self._pixmap = pixmap
        self.label.setPixmap(pixmap)
        self._rect = self._pixmap.rect()
        self._rect.translate(-self._rect.center())
        self.update()

    def scale(self, factor):
        self._scaleFactor *= factor
        self.label.resize(self._scaleFactor * self.label.pixmap().size())
        self.adjustScrollBar(self.scrollarea.horizontalScrollBar(), factor)
        self.adjustScrollBar(self.scrollarea.verticalScrollBar(), factor)
        self.update()

    def adjustScrollBar(self, scrollBar, factor):
        scrollBar.setValue(int(factor * scrollBar.value() + ((factor - 1) * scrollBar.pageStep()/2)))

    def sizeHint(self):
        return QSize(400, 400)

    @pyqtSlot()
    def pixmapReset(self):
        """Called when the pixmap is set back to original size."""
        self._scaleFactor = 1.0
        self.update()

    @pyqtSlot(QPointF)
    def slot_paint_event(self, delta):
        self._delta = delta
        self.update()
        print(f"{self} received signal from {self.sender()}")




from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem

class SceneImageViewer(QGraphicsView):
    """Re-Implementation test"""

    def __init__(self, parent):
        super().__init__(parent)
        self._scene = QGraphicsScene()
        self._item = QGraphicsPixmapItem()
        self.setScene(_scene)
        self._scene.addItem(self.item)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)

    def setPixmap(self, pixmap):
        self._item.setPixmap(pixmap)
        offset = -QRectF(pixmap.rect()).center()
        self._item.setOffset(offset)
        self.setSceneRect(offset.x()*4, offset.y()*4, -offset.x()*8, -offset.y()*8)
        self.translate(1, 1)

    def scale(self, factor):
        self.scale(factor, factor)

    def sizeHint():
        return QSize(400, 400)
