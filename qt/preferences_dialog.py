# Copyright 2016 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from PyQt5.QtCore import Qt, QSize, pyqtSlot
from PyQt5.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QComboBox,
    QSlider,
    QSizePolicy,
    QSpacerItem,
    QCheckBox,
    QLineEdit,
    QMessageBox,
    QSpinBox,
    QLayout,
    QTabWidget,
    QWidget,
    QColorDialog,
    QPushButton,
    QGroupBox,
    QFormLayout,
)
from PyQt5.QtGui import QPixmap, QIcon
from hscommon import plat

from hscommon.trans import trget
from hscommon.plat import ISLINUX
from qtlib.util import horizontal_wrap, move_to_screen_center
from qtlib.preferences import get_langnames
from enum import Flag, auto

from .preferences import Preferences

tr = trget("ui")

SUPPORTED_LANGUAGES = [
    "cs",
    "de",
    "el",
    "en",
    "es",
    "fr",
    "hy",
    "it",
    "ja",
    "ko",
    "ms",
    "nl",
    "pl_PL",
    "pt_BR",
    "ru",
    "tr",
    "uk",
    "vi",
    "zh_CN",
]


class Sections(Flag):
    """Filter blocks of preferences when reset or loaded"""

    GENERAL = auto()
    DISPLAY = auto()
    ALL = GENERAL | DISPLAY


class PreferencesDialogBase(QDialog):
    def __init__(self, parent, app, **kwargs):
        flags = Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowSystemMenuHint
        super().__init__(parent, flags, **kwargs)
        self.app = app
        all_languages = get_langnames()
        self.supportedLanguages = sorted(SUPPORTED_LANGUAGES, key=lambda lang: all_languages[lang])
        self._setupUi()

        self.filterHardnessSlider.valueChanged["int"].connect(self.filterHardnessLabel.setNum)
        self.buttonBox.clicked.connect(self.buttonClicked)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

    def _setupFilterHardnessBox(self):
        self.filterHardnessHLayout = QHBoxLayout()
        self.filterHardnessLabel = QLabel(self)
        self.filterHardnessLabel.setText(tr("Filter Hardness:"))
        self.filterHardnessLabel.setMinimumSize(QSize(0, 0))
        self.filterHardnessHLayout.addWidget(self.filterHardnessLabel)
        self.filterHardnessVLayout = QVBoxLayout()
        self.filterHardnessVLayout.setSpacing(0)
        self.filterHardnessHLayoutSub1 = QHBoxLayout()
        self.filterHardnessHLayoutSub1.setSpacing(12)
        self.filterHardnessSlider = QSlider(self)
        size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.filterHardnessSlider.sizePolicy().hasHeightForWidth())
        self.filterHardnessSlider.setSizePolicy(size_policy)
        self.filterHardnessSlider.setMinimum(1)
        self.filterHardnessSlider.setMaximum(100)
        self.filterHardnessSlider.setTracking(True)
        self.filterHardnessSlider.setOrientation(Qt.Horizontal)
        self.filterHardnessHLayoutSub1.addWidget(self.filterHardnessSlider)
        self.filterHardnessLabel = QLabel(self)
        self.filterHardnessLabel.setText("100")
        self.filterHardnessLabel.setMinimumSize(QSize(21, 0))
        self.filterHardnessHLayoutSub1.addWidget(self.filterHardnessLabel)
        self.filterHardnessVLayout.addLayout(self.filterHardnessHLayoutSub1)
        self.filterHardnessHLayoutSub2 = QHBoxLayout()
        self.filterHardnessHLayoutSub2.setContentsMargins(-1, 0, -1, -1)
        self.moreResultsLabel = QLabel(self)
        self.moreResultsLabel.setText(tr("More Results"))
        self.filterHardnessHLayoutSub2.addWidget(self.moreResultsLabel)
        spacer_item = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.filterHardnessHLayoutSub2.addItem(spacer_item)
        self.fewerResultsLabel = QLabel(self)
        self.fewerResultsLabel.setText(tr("Fewer Results"))
        self.filterHardnessHLayoutSub2.addWidget(self.fewerResultsLabel)
        self.filterHardnessVLayout.addLayout(self.filterHardnessHLayoutSub2)
        self.filterHardnessHLayout.addLayout(self.filterHardnessVLayout)

    def _setupBottomPart(self):
        # The bottom part of the pref panel is always the same in all editions.
        self.copyMoveLabel = QLabel(self)
        self.copyMoveLabel.setText(tr("Copy and Move:"))
        self.widgetsVLayout.addWidget(self.copyMoveLabel)
        self.copyMoveDestinationComboBox = QComboBox(self)
        self.copyMoveDestinationComboBox.addItem(tr("Right in destination"))
        self.copyMoveDestinationComboBox.addItem(tr("Recreate relative path"))
        self.copyMoveDestinationComboBox.addItem(tr("Recreate absolute path"))
        self.widgetsVLayout.addWidget(self.copyMoveDestinationComboBox)
        self.customCommandLabel = QLabel(self)
        self.customCommandLabel.setText(tr("Custom Command (arguments: %d for dupe, %r for ref):"))
        self.widgetsVLayout.addWidget(self.customCommandLabel)
        self.customCommandEdit = QLineEdit(self)
        self.widgetsVLayout.addWidget(self.customCommandEdit)

    def _setupDisplayPage(self):
        self.ui_groupbox = QGroupBox("&" + tr("General Interface"))
        layout = QVBoxLayout()
        self.languageLabel = QLabel(tr("Language:"), self)
        self.languageComboBox = QComboBox(self)
        for lang in self.supportedLanguages:
            self.languageComboBox.addItem(get_langnames()[lang])
        layout.addLayout(horizontal_wrap([self.languageLabel, self.languageComboBox, None]))
        self._setupAddCheckbox(
            "tabs_default_pos",
            tr("Use default position for tab bar (requires restart)"),
        )
        self.tabs_default_pos.setToolTip(
            tr(
                "Place the tab bar below the main menu instead of next to it\n\
On MacOS, the tab bar will fill up the window's width instead."
            )
        )
        layout.addWidget(self.tabs_default_pos)
        self._setupAddCheckbox(
            "use_native_dialogs",
            tr("Use native OS dialogs"),
        )
        self.use_native_dialogs.setToolTip(
            tr(
                "For actions such as file/folder selection use the OS native dialogs.\nSome native dialogs have limited functionality."
            )
        )
        layout.addWidget(self.use_native_dialogs)
        if plat.ISWINDOWS:
            self._setupAddCheckbox("use_dark_style", tr("Use dark style"))
            layout.addWidget(self.use_dark_style)
        self.ui_groupbox.setLayout(layout)
        self.displayVLayout.addWidget(self.ui_groupbox)

        gridlayout = QGridLayout()
        gridlayout.setColumnStretch(2, 2)
        formlayout = QFormLayout()
        result_groupbox = QGroupBox("&" + tr("Result Table"))
        self.fontSizeSpinBox = QSpinBox()
        self.fontSizeSpinBox.setMinimum(5)
        formlayout.addRow(tr("Font size:"), self.fontSizeSpinBox)
        self._setupAddCheckbox("reference_bold_font", tr("Use bold font for references"))
        formlayout.addRow(self.reference_bold_font)

        self.result_table_ref_foreground_color = ColorPickerButton(self)
        formlayout.addRow(tr("Reference foreground color:"), self.result_table_ref_foreground_color)
        self.result_table_ref_background_color = ColorPickerButton(self)
        formlayout.addRow(tr("Reference background color:"), self.result_table_ref_background_color)
        self.result_table_delta_foreground_color = ColorPickerButton(self)
        formlayout.addRow(tr("Delta foreground color:"), self.result_table_delta_foreground_color)
        formlayout.setLabelAlignment(Qt.AlignLeft)

        # Keep same vertical spacing as parent layout for consistency
        formlayout.setVerticalSpacing(self.displayVLayout.spacing())
        gridlayout.addLayout(formlayout, 0, 0)
        result_groupbox.setLayout(gridlayout)
        self.displayVLayout.addWidget(result_groupbox)

        details_groupbox = QGroupBox("&" + tr("Details Window"))
        self.details_groupbox_layout = QVBoxLayout()
        self._setupAddCheckbox(
            "details_dialog_titlebar_enabled",
            tr("Show the title bar and can be docked"),
        )
        self.details_dialog_titlebar_enabled.setToolTip(
            tr(
                "While the title bar is hidden, \
use the modifier key to drag the floating window around"
            )
            if ISLINUX
            else tr("The title bar can only be disabled while the window is docked")
        )
        self.details_groupbox_layout.addWidget(self.details_dialog_titlebar_enabled)
        self._setupAddCheckbox("details_dialog_vertical_titlebar", tr("Vertical title bar"))
        self.details_dialog_vertical_titlebar.setToolTip(
            tr("Change the title bar from horizontal on top, to vertical on the left side")
        )
        self.details_groupbox_layout.addWidget(self.details_dialog_vertical_titlebar)
        self.details_dialog_vertical_titlebar.setEnabled(self.details_dialog_titlebar_enabled.isChecked())
        self.details_dialog_titlebar_enabled.stateChanged.connect(self.details_dialog_vertical_titlebar.setEnabled)
        gridlayout = QGridLayout()
        formlayout = QFormLayout()
        self.details_table_delta_foreground_color = ColorPickerButton(self)
        # Padding on the right side and space between label and widget to keep it somewhat consistent across themes
        gridlayout.setColumnStretch(1, 1)
        formlayout.setHorizontalSpacing(50)
        formlayout.addRow(tr("Delta foreground color:"), self.details_table_delta_foreground_color)
        gridlayout.addLayout(formlayout, 0, 0)
        self.details_groupbox_layout.addLayout(gridlayout)
        details_groupbox.setLayout(self.details_groupbox_layout)
        self.displayVLayout.addWidget(details_groupbox)

    def _setupAddCheckbox(self, name, label, parent=None):
        if parent is None:
            parent = self
        cb = QCheckBox(parent)
        cb.setText(label)
        setattr(self, name, cb)

    def _setupPreferenceWidgets(self):
        # Edition-specific
        pass

    def _setupUi(self):
        self.setWindowTitle(tr("Options"))
        self.setSizeGripEnabled(False)
        self.setModal(True)
        self.mainVLayout = QVBoxLayout(self)
        self.tabwidget = QTabWidget()
        self.page_general = QWidget()
        self.page_display = QWidget()
        self.widgetsVLayout = QVBoxLayout()
        self.page_general.setLayout(self.widgetsVLayout)
        self.displayVLayout = QVBoxLayout()
        self.displayVLayout.setSpacing(5)  # arbitrary value, might conflict with style
        self.page_display.setLayout(self.displayVLayout)
        self._setupPreferenceWidgets()
        self._setupDisplayPage()
        # self.mainVLayout.addLayout(self.widgetsVLayout)
        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setStandardButtons(
            QDialogButtonBox.Cancel | QDialogButtonBox.Ok | QDialogButtonBox.RestoreDefaults
        )
        self.mainVLayout.addWidget(self.tabwidget)
        self.mainVLayout.addWidget(self.buttonBox)
        self.layout().setSizeConstraint(QLayout.SetFixedSize)
        self.tabwidget.addTab(self.page_general, tr("General"))
        self.tabwidget.addTab(self.page_display, tr("Display"))
        self.displayVLayout.addStretch(0)
        self.widgetsVLayout.addStretch(0)

    def _load(self, prefs, setchecked, section):
        # Edition-specific
        pass

    def _save(self, prefs, ischecked):
        # Edition-specific
        pass

    def load(self, prefs=None, section=Sections.ALL):
        if prefs is None:
            prefs = self.app.prefs

        def setchecked(cb, b):
            cb.setCheckState(Qt.Checked if b else Qt.Unchecked)

        if section & Sections.GENERAL:
            self.filterHardnessSlider.setValue(prefs.filter_hardness)
            self.filterHardnessLabel.setNum(prefs.filter_hardness)
            setchecked(self.mixFileKindBox, prefs.mix_file_kind)
            setchecked(self.useRegexpBox, prefs.use_regexp)
            setchecked(self.removeEmptyFoldersBox, prefs.remove_empty_folders)
            setchecked(self.ignoreHardlinkMatches, prefs.ignore_hardlink_matches)
            setchecked(self.debugModeBox, prefs.debug_mode)
            self.copyMoveDestinationComboBox.setCurrentIndex(prefs.destination_type)
            self.customCommandEdit.setText(prefs.custom_command)
        if section & Sections.DISPLAY:
            setchecked(self.reference_bold_font, prefs.reference_bold_font)
            setchecked(self.tabs_default_pos, prefs.tabs_default_pos)
            setchecked(self.use_native_dialogs, prefs.use_native_dialogs)
            if plat.ISWINDOWS:
                setchecked(self.use_dark_style, prefs.use_dark_style)
            setchecked(
                self.details_dialog_titlebar_enabled,
                prefs.details_dialog_titlebar_enabled,
            )
            setchecked(
                self.details_dialog_vertical_titlebar,
                prefs.details_dialog_vertical_titlebar,
            )
            self.fontSizeSpinBox.setValue(prefs.tableFontSize)
            self.details_table_delta_foreground_color.setColor(prefs.details_table_delta_foreground_color)
            self.result_table_ref_foreground_color.setColor(prefs.result_table_ref_foreground_color)
            self.result_table_ref_background_color.setColor(prefs.result_table_ref_background_color)
            self.result_table_delta_foreground_color.setColor(prefs.result_table_delta_foreground_color)
            try:
                langindex = self.supportedLanguages.index(self.app.prefs.language)
            except ValueError:
                langindex = 0
            self.languageComboBox.setCurrentIndex(langindex)
        self._load(prefs, setchecked, section)

    def save(self):
        prefs = self.app.prefs
        prefs.filter_hardness = self.filterHardnessSlider.value()

        def ischecked(cb):
            return cb.checkState() == Qt.Checked

        prefs.mix_file_kind = ischecked(self.mixFileKindBox)
        prefs.use_regexp = ischecked(self.useRegexpBox)
        prefs.remove_empty_folders = ischecked(self.removeEmptyFoldersBox)
        prefs.ignore_hardlink_matches = ischecked(self.ignoreHardlinkMatches)
        prefs.debug_mode = ischecked(self.debugModeBox)
        prefs.reference_bold_font = ischecked(self.reference_bold_font)
        prefs.details_dialog_titlebar_enabled = ischecked(self.details_dialog_titlebar_enabled)
        prefs.details_dialog_vertical_titlebar = ischecked(self.details_dialog_vertical_titlebar)
        prefs.details_table_delta_foreground_color = self.details_table_delta_foreground_color.color
        prefs.result_table_ref_foreground_color = self.result_table_ref_foreground_color.color
        prefs.result_table_ref_background_color = self.result_table_ref_background_color.color
        prefs.result_table_delta_foreground_color = self.result_table_delta_foreground_color.color
        prefs.destination_type = self.copyMoveDestinationComboBox.currentIndex()
        prefs.custom_command = str(self.customCommandEdit.text())
        prefs.tableFontSize = self.fontSizeSpinBox.value()
        prefs.tabs_default_pos = ischecked(self.tabs_default_pos)
        prefs.use_native_dialogs = ischecked(self.use_native_dialogs)
        if plat.ISWINDOWS:
            prefs.use_dark_style = ischecked(self.use_dark_style)
        lang = self.supportedLanguages[self.languageComboBox.currentIndex()]
        oldlang = self.app.prefs.language
        if oldlang not in self.supportedLanguages:
            oldlang = "en"
        if lang != oldlang:
            QMessageBox.information(
                self,
                "",
                tr("dupeGuru has to restart for language changes to take effect."),
            )
        self.app.prefs.language = lang
        self._save(prefs, ischecked)

    def resetToDefaults(self, section_to_update):
        self.load(Preferences(), section_to_update)

    # --- Events
    def buttonClicked(self, button):
        role = self.buttonBox.buttonRole(button)
        if role == QDialogButtonBox.ResetRole:
            current_tab = self.tabwidget.currentWidget()
            section_to_update = Sections.ALL
            if current_tab is self.page_general:
                section_to_update = Sections.GENERAL
            if current_tab is self.page_display:
                section_to_update = Sections.DISPLAY
            self.resetToDefaults(section_to_update)

    def showEvent(self, event):
        # have to do this here as the frameGeometry is not correct until shown
        move_to_screen_center(self)
        super().showEvent(event)


class ColorPickerButton(QPushButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.color = None
        self.clicked.connect(self.onClicked)

    @pyqtSlot()
    def onClicked(self):
        color = QColorDialog.getColor(self.color if self.color is not None else Qt.white, self.parent)
        self.setColor(color)

    def setColor(self, color):
        size = QSize(16, 16)
        px = QPixmap(size)
        if color is None:
            size.width = 0
            size.height = 0
        elif not color.isValid():
            return
        else:
            self.color = color
            px.fill(color)
        self.setIcon(QIcon(px))
