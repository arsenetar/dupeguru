# Copyright 2016 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QVBoxLayout,
    QHBoxLayout,
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
)

from hscommon.trans import trget
from qtlib.util import horizontalWrap
from qtlib.preferences import get_langnames
from enum import Flag, auto

from .preferences import Preferences

tr = trget("ui")

SUPPORTED_LANGUAGES = [
    "en",
    "fr",
    "de",
    "el",
    "zh_CN",
    "cs",
    "it",
    "hy",
    "ru",
    "uk",
    "pt_BR",
    "vi",
    "pl_PL",
    "ko",
    "es",
    "nl",
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
        self.supportedLanguages = sorted(
            SUPPORTED_LANGUAGES, key=lambda lang: all_languages[lang]
        )
        self._setupUi()

        self.filterHardnessSlider.valueChanged["int"].connect(
            self.filterHardnessLabel.setNum
        )
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
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.filterHardnessSlider.sizePolicy().hasHeightForWidth()
        )
        self.filterHardnessSlider.setSizePolicy(sizePolicy)
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
        spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.filterHardnessHLayoutSub2.addItem(spacerItem)
        self.fewerResultsLabel = QLabel(self)
        self.fewerResultsLabel.setText(tr("Fewer Results"))
        self.filterHardnessHLayoutSub2.addWidget(self.fewerResultsLabel)
        self.filterHardnessVLayout.addLayout(self.filterHardnessHLayoutSub2)
        self.filterHardnessHLayout.addLayout(self.filterHardnessVLayout)

    def _setupBottomPart(self):
        # The bottom part of the pref panel is always the same in all editions.
        self._setupDisplayPage()
        self.copyMoveLabel = QLabel(self)
        self.copyMoveLabel.setText(tr("Copy and Move:"))
        self.widgetsVLayout.addWidget(self.copyMoveLabel)
        self.copyMoveDestinationComboBox = QComboBox(self)
        self.copyMoveDestinationComboBox.addItem(tr("Right in destination"))
        self.copyMoveDestinationComboBox.addItem(tr("Recreate relative path"))
        self.copyMoveDestinationComboBox.addItem(tr("Recreate absolute path"))
        self.widgetsVLayout.addWidget(self.copyMoveDestinationComboBox)
        self.customCommandLabel = QLabel(self)
        self.customCommandLabel.setText(
            tr("Custom Command (arguments: %d for dupe, %r for ref):")
        )
        self.widgetsVLayout.addWidget(self.customCommandLabel)
        self.customCommandEdit = QLineEdit(self)
        self.widgetsVLayout.addWidget(self.customCommandEdit)

    def _setupDisplayPage(self):
        self.fontSizeLabel = QLabel(tr("Font size:"))
        self.fontSizeSpinBox = QSpinBox()
        self.fontSizeSpinBox.setMinimum(5)
        self.displayVLayout.addLayout(
            horizontalWrap([self.fontSizeLabel, self.fontSizeSpinBox, None])
        )
        self._setupAddCheckbox("reference_bold_font",
                               tr("Bold font for reference"))
        self.displayVLayout.addWidget(self.reference_bold_font)

        self.details_dialog_label = QLabel(tr("Details window:"))
        self.displayVLayout.addWidget(self.details_dialog_label)
        self._setupAddCheckbox("details_dialog_titlebar_enabled",
                               tr("Show a title bar and is dockable"))
        self.details_dialog_titlebar_enabled.setToolTip(
            tr("Title bar can only be disabled while the window is docked"))
        self.displayVLayout.addWidget(self.details_dialog_titlebar_enabled)
        self._setupAddCheckbox("details_dialog_vertical_titlebar",
                               tr("Vertical title bar"))
        self.displayVLayout.addWidget(self.details_dialog_vertical_titlebar)
        self.details_dialog_vertical_titlebar.setEnabled(
            self.details_dialog_titlebar_enabled.isChecked())
        self.details_dialog_titlebar_enabled.stateChanged.connect(
            self.details_dialog_vertical_titlebar.setEnabled)

        self.languageLabel = QLabel(tr("Language:"), self)
        self.languageComboBox = QComboBox(self)
        for lang in self.supportedLanguages:
            self.languageComboBox.addItem(get_langnames()[lang])
        self.displayVLayout.insertLayout(
            0, horizontalWrap([self.languageLabel, self.languageComboBox, None])
        )

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
        self.page_display.setLayout(self.displayVLayout)
        self._setupPreferenceWidgets()
        # self.mainVLayout.addLayout(self.widgetsVLayout)
        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setStandardButtons(
            QDialogButtonBox.Cancel
            | QDialogButtonBox.Ok
            | QDialogButtonBox.RestoreDefaults
        )
        self.mainVLayout.addWidget(self.tabwidget)
        self.mainVLayout.addWidget(self.buttonBox)
        self.layout().setSizeConstraint(QLayout.SetFixedSize)
        self.tabwidget.addTab(self.page_general, "General")
        self.tabwidget.addTab(self.page_display, "Display")
        self.displayVLayout.addStretch(0)

    def _load(self, prefs, setchecked, section):
        # Edition-specific
        pass

    def _save(self, prefs, ischecked):
        # Edition-specific
        pass

    def load(self, prefs=None, section=Sections.ALL):
        if prefs is None:
            prefs = self.app.prefs
        setchecked = lambda cb, b: cb.setCheckState(Qt.Checked if b else Qt.Unchecked)
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
            setchecked(self.details_dialog_titlebar_enabled , prefs.details_dialog_titlebar_enabled)
            setchecked(self.details_dialog_vertical_titlebar, prefs.details_dialog_vertical_titlebar)
            self.fontSizeSpinBox.setValue(prefs.tableFontSize)
            try:
                langindex = self.supportedLanguages.index(self.app.prefs.language)
            except ValueError:
                langindex = 0
            self.languageComboBox.setCurrentIndex(langindex)
        self._load(prefs, setchecked, section)

    def save(self):
        prefs = self.app.prefs
        prefs.filter_hardness = self.filterHardnessSlider.value()
        ischecked = lambda cb: cb.checkState() == Qt.Checked
        prefs.mix_file_kind = ischecked(self.mixFileKindBox)
        prefs.use_regexp = ischecked(self.useRegexpBox)
        prefs.remove_empty_folders = ischecked(self.removeEmptyFoldersBox)
        prefs.ignore_hardlink_matches = ischecked(self.ignoreHardlinkMatches)
        prefs.debug_mode = ischecked(self.debugModeBox)
        prefs.reference_bold_font = ischecked(self.reference_bold_font)
        prefs.details_dialog_titlebar_enabled = ischecked(self.details_dialog_titlebar_enabled)
        prefs.details_dialog_vertical_titlebar = ischecked(self.details_dialog_vertical_titlebar)
        prefs.destination_type = self.copyMoveDestinationComboBox.currentIndex()
        prefs.custom_command = str(self.customCommandEdit.text())
        prefs.tableFontSize = self.fontSizeSpinBox.value()
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
