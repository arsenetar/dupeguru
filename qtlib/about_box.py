# Created By: Virgil Dupras
# Created On: 2009-05-09
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from PyQt5.QtCore import Qt, QCoreApplication, QTimer
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QSizePolicy, QHBoxLayout, QVBoxLayout, QLabel

from core.util import check_for_update
from qtlib.util import move_to_screen_center
from hscommon.trans import trget

tr = trget("qtlib")


class AboutBox(QDialog):
    def __init__(self, parent, app, **kwargs):
        flags = Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowSystemMenuHint | Qt.MSWindowsFixedSizeDialogHint
        super().__init__(parent, flags, **kwargs)
        self.app = app
        self._setupUi()

        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

    def _setupUi(self):
        self.setWindowTitle(tr("About {}").format(QCoreApplication.instance().applicationName()))
        size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setSizePolicy(size_policy)
        main_layout = QHBoxLayout(self)
        logo_label = QLabel()
        logo_label.setPixmap(QPixmap(":/%s_big" % self.app.LOGO_NAME))
        main_layout.addWidget(logo_label)
        detail_layout = QVBoxLayout()
        name_label = QLabel()
        font = QFont()
        font.setWeight(75)
        font.setBold(True)
        name_label.setFont(font)
        name_label.setText(QCoreApplication.instance().applicationName())
        detail_layout.addWidget(name_label)
        version_label = QLabel()
        version_label.setText(tr("Version {}").format(QCoreApplication.instance().applicationVersion()))
        detail_layout.addWidget(version_label)
        self.update_label = QLabel(tr("Checking for updates..."))
        self.update_label.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.update_label.setOpenExternalLinks(True)
        detail_layout.addWidget(self.update_label)
        license_label = QLabel()
        license_label.setText(tr("Licensed under GPLv3"))
        detail_layout.addWidget(license_label)
        spacer_label = QLabel()
        spacer_label.setFont(font)
        detail_layout.addWidget(spacer_label)
        self.button_box = QDialogButtonBox()
        self.button_box.setOrientation(Qt.Horizontal)
        self.button_box.setStandardButtons(QDialogButtonBox.Ok)
        detail_layout.addWidget(self.button_box)
        main_layout.addLayout(detail_layout)

    def _check_for_update(self):
        update = check_for_update(QCoreApplication.instance().applicationVersion(), include_prerelease=False)
        if update is None:
            self.update_label.setText(tr("No update available."))
        else:
            self.update_label.setText(
                tr('New version {} available, download <a href="{}">here</a>.').format(update["version"], update["url"])
            )

    def showEvent(self, event):
        self.update_label.setText(tr("Checking for updates..."))
        # have to do this here as the frameGeometry is not correct until shown
        move_to_screen_center(self)
        super().showEvent(event)
        QTimer.singleShot(0, self._check_for_update)
