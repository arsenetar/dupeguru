# Created By: Virgil Dupras
# Created On: 2009-12-10
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4.QtCore import pyqtSignal, Qt
from PyQt4.QtGui import (QToolButton, QLineEdit, QIcon, QPixmap, QStyle, QStyleOptionFrameV2,
    QPainter, QPalette)

from hscommon.trans import trget

tr = trget('qtlib')

# IMPORTANT: For this widget to work propertly, you have to add "search_clear_13" from the
# "images" folder in your resources.

class LineEditButton(QToolButton):
    def __init__(self, parent):
        QToolButton.__init__(self, parent)
        pixmap = QPixmap(':/search_clear_13')
        self.setIcon(QIcon(pixmap))
        self.setIconSize(pixmap.size())
        self.setCursor(Qt.ArrowCursor)
        self.setPopupMode(QToolButton.InstantPopup)
        stylesheet = "QToolButton { border: none; padding: 0px; }"
        self.setStyleSheet(stylesheet)
    

class SearchEdit(QLineEdit):
    def __init__(self, parent=None, immediate=False):
        # immediate: send searchChanged signals at each keystroke.
        QLineEdit.__init__(self, parent)
        self._clearButton = LineEditButton(self)
        frameWidth = self.style().pixelMetric(QStyle.PM_DefaultFrameWidth)
        paddingRight = self._clearButton.sizeHint().width() + frameWidth + 1
        stylesheet = "QLineEdit {{ padding-right:{0}px; }}".format(paddingRight)
        self.setStyleSheet(stylesheet)
        self.inactiveText = tr("Search...")
        self.immediate = immediate
        self._updateClearButton(self.text())
        
        self._clearButton.clicked.connect(self._clearSearch)
        self.returnPressed.connect(self._returnPressed)
        self.textChanged.connect(self._textChanged)
    
    #--- Private
    def _clearSearch(self):
        self.clear()
        self.searchChanged.emit()
    
    def _updateClearButton(self, text):
        self._clearButton.setVisible(bool(text))
    
    #--- QLineEdit overrides
    def resizeEvent(self, event):
        frameWidth = self.style().pixelMetric(QStyle.PM_DefaultFrameWidth)
        rect = self.rect()
        rightHint = self._clearButton.sizeHint()
        rightX = rect.right() - frameWidth - rightHint.width()
        rightY = (rect.bottom() - rightHint.height()) // 2
        self._clearButton.move(rightX, rightY)
    
    def paintEvent(self, event):
        QLineEdit.paintEvent(self, event)
        if not bool(self.text()) and self.inactiveText and not self.hasFocus():
            panel = QStyleOptionFrameV2()
            self.initStyleOption(panel)
            textRect = self.style().subElementRect(QStyle.SE_LineEditContents, panel, self)
            leftMargin = 2
            rightMargin = self._clearButton.iconSize().width()
            textRect.adjust(leftMargin, 0, -rightMargin, 0)
            painter = QPainter(self)
            disabledColor = self.palette().brush(QPalette.Disabled, QPalette.Text).color()
            painter.setPen(disabledColor)
            painter.drawText(textRect, Qt.AlignLeft|Qt.AlignVCenter, self.inactiveText)
    
    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Escape:
            self._clearSearch()
        else:
            QLineEdit.keyPressEvent(self, event)
    
    #--- Event Handlers
    def _returnPressed(self):
        if not self.immediate:
            self.searchChanged.emit()
    
    def _textChanged(self, text):
        self._updateClearButton(text)
        if self.immediate:
            self.searchChanged.emit()
    
    #--- Signals
    searchChanged = pyqtSignal() # Emitted when return is pressed or when the test is cleared
