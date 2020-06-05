# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from PyQt5.QtCore import Qt, QSize, QRectF, QPointF, pyqtSlot, pyqtSignal, QEvent
from PyQt5.QtGui import QPixmap, QPainter, QPalette
from PyQt5.QtWidgets import ( QLabel, QSizePolicy, QWidget, QScrollArea, 
                              QApplication, QAbstractScrollArea )

class ImageViewer(QWidget):
    """Displays image and allows manipulations."""
    mouseMoved = pyqtSignal(QPointF)

    def __init__(self, parent, name=""):
        super().__init__(parent)
        self.parent = parent
        self.app = QApplication
        self.pixmap = QPixmap()
        self.m_rect = QRectF()
        self.reference = QPointF()
        self.delta = QPointF()
        self.scalefactor = 1.0
        self.drag = False
        self.connection = None # signal bound to a slot
        self.instance_name = name

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

    def __repr__(self):
        return f'{self.instance_name}'

    @pyqtSlot(QPointF)
    def slot_paint_event(self, delta):
        self.delta = delta
        self.update()
        print(f"{self} received signal from {self.sender()}")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.translate(self.rect().center())
        painter.scale(self.scalefactor, self.scalefactor)
        painter.translate(self.delta)
        painter.drawPixmap(self.m_rect.topLeft(), self.pixmap)
        # print(f"{self} paintEvent delta={self.delta}")

    def setCenter(self):
        """ Resets origin """
        self.delta = QPointF()
        self.scalefactor = 1.0
        self.scale(self.scalefactor)
        self.update()

    def changeEvent(self, event):
        if event.type() == QEvent.EnabledChange:
            print(f"{self} is now {'enabled' if self.isEnabled() else 'disabled'}")

    def mousePressEvent(self, event):
        if self.parent.bestFit:
            event.ignore()
            return
        if event.buttons() == Qt.LeftButton:
            self.drag = True

        self.reference = event.pos()
        self.app.setOverrideCursor(Qt.ClosedHandCursor)
        self.setMouseTracking(True)

    def mouseMoveEvent(self, event):
        if self.parent.bestFit:
            event.ignore()
            return

        self.delta += (event.pos() - self.reference) * 1.0/self.scalefactor
        self.reference = event.pos()
        if self.drag:
            self.mouseMoved.emit(self.delta)
        self.update()

    def mouseReleaseEvent(self, event):
        if self.parent.bestFit:
            event.ignore()
            return
        if event.buttons() == Qt.LeftButton:
            drag = False

        self.app.restoreOverrideCursor()
        self.setMouseTracking(False)

    def wheelEvent(self, event):
        if self.parent.bestFit:
            event.ignore()
            return

        if event.angleDelta().y() > 0:
            self.parent.zoomIn()
        else:
            self.parent.zoomOut()

    def setPixmap(self, pixmap):
        if pixmap.isNull():
            if not self.pixmap.isNull():
                self.pixmap = pixmap
                self.update()
            return
        elif not self.isEnabled():
            self.setEnabled(True)
        self.pixmap = pixmap
        self.m_rect = self.pixmap.rect()
        self.m_rect.translate(-self.m_rect.center())
        self.update()

    def scale(self, factor):
        self.scalefactor = factor
        # self.label.resize(self.scalefactor * self.label.size())
        self.update()

    def sizeHint(self):
        return QSize(400, 400)

    @pyqtSlot()
    def pixmapReset(self):
        """Called when the pixmap is set back to original size."""
        self.scalefactor = 1.0
        self.update()