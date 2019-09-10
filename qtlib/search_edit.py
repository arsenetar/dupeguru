# Created By: Virgil Dupras
# Created On: 2009-12-10
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QPalette
from PyQt5.QtWidgets import QToolButton, QLineEdit, QStyle, QStyleOptionFrame

from hscommon.trans import trget

tr = trget('qtlib')

# IMPORTANT: For this widget to work propertly, you have to add "search_clear_13" from the
# "images" folder in your resources.

class LineEditButton(QToolButton):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        pixmap = QPixmap(':/search_clear_13')
        self.setIcon(QIcon(pixmap))
        self.setIconSize(pixmap.size())
        self.setCursor(Qt.ArrowCursor)
        self.setPopupMode(QToolButton.InstantPopup)
        stylesheet = "QToolButton { border: none; padding: 0px; }"
        self.setStyleSheet(stylesheet)


class ClearableEdit(QLineEdit):
    def __init__(self, parent=None, is_clearable=True, **kwargs):
        super().__init__(parent, **kwargs)
        self._is_clearable = is_clearable
        if is_clearable:
            self._clearButton = LineEditButton(self)
            frameWidth = self.style().pixelMetric(QStyle.PM_DefaultFrameWidth)
            paddingRight = self._clearButton.sizeHint().width() + frameWidth + 1
            stylesheet = "QLineEdit {{ padding-right:{0}px; }}".format(paddingRight)
            self.setStyleSheet(stylesheet)
            self._updateClearButton()

            self._clearButton.clicked.connect(self._clearSearch)
        self.textChanged.connect(self._textChanged)

    #--- Private
    def _clearSearch(self):
        self.clear()

    def _updateClearButton(self):
        self._clearButton.setVisible(self._hasClearableContent())

    def _hasClearableContent(self):
        return bool(self.text())

    #--- QLineEdit overrides
    def resizeEvent(self, event):
        if self._is_clearable:
            frameWidth = self.style().pixelMetric(QStyle.PM_DefaultFrameWidth)
            rect = self.rect()
            rightHint = self._clearButton.sizeHint()
            rightX = rect.right() - frameWidth - rightHint.width()
            rightY = (rect.bottom() - rightHint.height()) // 2
            self._clearButton.move(rightX, rightY)

    #--- Event Handlers
    def _textChanged(self, text):
        if self._is_clearable:
            self._updateClearButton()


class SearchEdit(ClearableEdit):
    def __init__(self, parent=None, immediate=False):
        # immediate: send searchChanged signals at each keystroke.
        ClearableEdit.__init__(self, parent, is_clearable=True)
        self.inactiveText = tr("Search...")
        self.immediate = immediate

        self.returnPressed.connect(self._returnPressed)

    #--- Overrides
    def _clearSearch(self):
        ClearableEdit._clearSearch(self)
        self.searchChanged.emit()

    def _textChanged(self, text):
        ClearableEdit._textChanged(self, text)
        if self.immediate:
            self.searchChanged.emit()

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Escape:
            self._clearSearch()
        else:
            ClearableEdit.keyPressEvent(self, event)

    def paintEvent(self, event):
        ClearableEdit.paintEvent(self, event)
        if not bool(self.text()) and self.inactiveText and not self.hasFocus():
            panel = QStyleOptionFrame()
            self.initStyleOption(panel)
            textRect = self.style().subElementRect(QStyle.SE_LineEditContents, panel, self)
            leftMargin = 2
            rightMargin = self._clearButton.iconSize().width()
            textRect.adjust(leftMargin, 0, -rightMargin, 0)
            painter = QPainter(self)
            disabledColor = self.palette().brush(QPalette.Disabled, QPalette.Text).color()
            painter.setPen(disabledColor)
            painter.drawText(textRect, Qt.AlignLeft|Qt.AlignVCenter, self.inactiveText)

    #--- Event Handlers
    def _returnPressed(self):
        if not self.immediate:
            self.searchChanged.emit()

    #--- Signals
    searchChanged = pyqtSignal() # Emitted when return is pressed or when the test is cleared

