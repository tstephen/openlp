# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2018 OpenLP Developers                                   #
# --------------------------------------------------------------------------- #
# This program is free software; you can redistribute it and/or modify it     #
# under the terms of the GNU General Public License as published by the Free  #
# Software Foundation; version 2 of the License.                              #
#                                                                             #
# This program is distributed in the hope that it will be useful, but WITHOUT #
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or       #
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for    #
# more details.                                                               #
#                                                                             #
# You should have received a copy of the GNU General Public License along     #
# with this program; if not, write to the Free Software Foundation, Inc., 59  #
# Temple Place, Suite 330, Boston, MA 02111-1307 USA                          #
###############################################################################
"""
The screen settings tab in the configuration dialog
"""
import logging

from PyQt5 import QtCore, QtWidgets

from openlp.core.common.i18n import translate
from openlp.core.common.settings import Settings
from openlp.core.display.screens import ScreenList
from openlp.core.lib.settingstab import SettingsTab
from openlp.core.ui.icons import UiIcons


SCREENS_LAYOUT_STYLE = """
#screen_frame {
  background-color: palette(base);
}
#screen_frame QPushButton  {
  background-color: palette(window);
  border: 3px solid palette(text);
  border-radius: 3px;
  height: 100px;
  outline: 0;
  width: 150px;
}
#screen_frame QPushButton:checked  {
    border-color: palette(highlight);
}
"""
log = logging.getLogger(__name__)


class ScreenButton(QtWidgets.QPushButton):
    """
    A special button class that holds the screen information about it
    """
    def __init__(self, parent, screen):
        """
        Initialise this button
        """
        super(ScreenButton, self).__init__(parent)
        self.setObjectName('screen{number}_button'.format(number=screen.number))
        self.setText(str(screen))
        self.setCheckable(True)
        self.screen = screen


class ScreensTab(SettingsTab):
    """
    ScreensTab is the screen settings tab in the configuration dialog
    """
    def __init__(self, parent):
        """
        Initialise the screen settings tab
        """
        self.screens = ScreenList()
        self.icon_path = UiIcons().settings
        screens_translated = translate('OpenLP.ScreensTab', 'Screens')
        super(ScreensTab, self).__init__(parent, 'Screens', screens_translated)
        self.settings_section = 'core'
        self.current_screen = None
        self.identify_labels = []

    def setup_ui(self):
        """
        Set up the user interface elements
        """
        self.setObjectName('self')
        self.setStyleSheet(SCREENS_LAYOUT_STYLE)
        self.tab_layout = QtWidgets.QVBoxLayout(self)
        self.tab_layout.setObjectName('tab_layout')
        self.screen_frame = QtWidgets.QFrame(self)
        self.screen_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.screen_frame.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.screen_frame.setObjectName('screen_frame')
        self.screen_frame_layout = QtWidgets.QHBoxLayout(self.screen_frame)
        self.screen_frame_layout.setContentsMargins(16, 16, 16, 16)
        self.screen_frame_layout.setSpacing(8)
        self.screen_frame_layout.setObjectName('screen_frame_layout')
        self.tab_layout.addWidget(self.screen_frame)
        self.screen_details_widget = QtWidgets.QWidget(self)
        self.screen_details_widget.setObjectName('screen_details_widget')
        self.screen_details_layout = QtWidgets.QGridLayout(self.screen_details_widget)
        self.screen_details_layout.setSpacing(8)
        self.screen_details_layout.setObjectName('screen_details_layout')
        self.screen_number_label = QtWidgets.QLabel(self.screen_details_widget)
        self.screen_number_label.setObjectName('screen_number_label')
        self.screen_details_layout.addWidget(self.screen_number_label, 0, 0, 1, 4)
        self.is_display_check_box = QtWidgets.QCheckBox(self.screen_details_widget)
        self.is_display_check_box.setObjectName('is_display_check_box')
        self.screen_details_layout.addWidget(self.is_display_check_box, 1, 0, 1, 4)
        self.full_screen_radio_button = QtWidgets.QRadioButton(self.screen_details_widget)
        self.full_screen_radio_button.setObjectName('full_screen_radio_button')
        self.screen_details_layout.addWidget(self.full_screen_radio_button, 2, 0, 1, 4)
        self.custom_geometry_button = QtWidgets.QRadioButton(self.screen_details_widget)
        self.custom_geometry_button.setObjectName('custom_geometry_button')
        self.screen_details_layout.addWidget(self.custom_geometry_button, 3, 0, 1, 4)
        self.left_label = QtWidgets.QLabel(self.screen_details_widget)
        self.left_label.setObjectName('left_label')
        self.screen_details_layout.addWidget(self.left_label, 4, 1, 1, 1)
        self.top_label = QtWidgets.QLabel(self.screen_details_widget)
        self.top_label.setObjectName('top_label')
        self.screen_details_layout.addWidget(self.top_label, 4, 2, 1, 1)
        self.width_label = QtWidgets.QLabel(self.screen_details_widget)
        self.width_label.setObjectName('width_label')
        self.screen_details_layout.addWidget(self.width_label, 4, 3, 1, 1)
        self.height_label = QtWidgets.QLabel(self.screen_details_widget)
        self.height_label.setObjectName('height_label')
        self.screen_details_layout.addWidget(self.height_label, 4, 4, 1, 1)
        self.left_spin_box = QtWidgets.QSpinBox(self.screen_details_widget)
        self.left_spin_box.setObjectName('left_spin_box')
        self.screen_details_layout.addWidget(self.left_spin_box, 5, 1, 1, 1)
        self.top_spin_box = QtWidgets.QSpinBox(self.screen_details_widget)
        self.top_spin_box.setObjectName('top_spin_box')
        self.screen_details_layout.addWidget(self.top_spin_box, 5, 2, 1, 1)
        self.width_spin_box = QtWidgets.QSpinBox(self.screen_details_widget)
        self.width_spin_box.setObjectName('width_spin_box')
        self.screen_details_layout.addWidget(self.width_spin_box, 5, 3, 1, 1)
        self.height_spin_box = QtWidgets.QSpinBox(self.screen_details_widget)
        self.height_spin_box.setObjectName('height_spin_box')
        self.screen_details_layout.addWidget(self.height_spin_box, 5, 4, 1, 1)
        self.screen_details_layout.setColumnStretch(5, 1)
        self.tab_layout.addWidget(self.screen_details_widget)
        self.tab_layout.addStretch()
        self.identify_button = QtWidgets.QPushButton(self)
        self.identify_button.setGeometry(QtCore.QRect(596, 98, 124, 32))
        self.identify_button.setObjectName('identify_button')
        self.screen_button_group = QtWidgets.QButtonGroup(self.screen_frame)
        self.screen_button_group.setExclusive(True)
        self.screen_button_group.setObjectName('screen_button_group')

        # Signals and slots
        # self.screen_combo_box.currentIndexChanged.connect(self.on_display_changed)
        # self.override_radio_button.toggled.connect(self.on_override_radio_button_pressed)
        # self.custom_height_value_edit.valueChanged.connect(self.on_display_changed)
        # self.custom_width_value_edit.valueChanged.connect(self.on_display_changed)
        # self.custom_Y_value_edit.valueChanged.connect(self.on_display_changed)
        # self.custom_X_value_edit.valueChanged.connect(self.on_display_changed)
        # Reload the tab, as the screen resolution/count may have changed.
        # Registry().register_function('config_screen_changed', self.load)
        self.identify_button.clicked.connect(self.on_identify_button_clicked)

        self._setup_spin_box(self.left_spin_box, 0, 9999, 0)
        self._setup_spin_box(self.top_spin_box, 0, 9999, 0)
        self._setup_spin_box(self.width_spin_box, 0, 9999, 0)
        self._setup_spin_box(self.height_spin_box, 0, 9999, 0)

        self.retranslate_ui()

    def retranslate_ui(self):
        self.setWindowTitle(translate('self', 'self'))
        self.full_screen_radio_button.setText(translate('OpenLP.ScreensTab', 'F&ull screen'))
        self.width_label.setText(translate('OpenLP.ScreensTab', 'Width:'))
        self.is_display_check_box.setText(translate('OpenLP.ScreensTab', 'Use this screen as a display'))
        self.left_label.setText(translate('OpenLP.ScreensTab', 'Left:'))
        self.custom_geometry_button.setText(translate('OpenLP.ScreensTab', 'Custom &geometry'))
        self.top_label.setText(translate('OpenLP.ScreensTab', 'Top:'))
        self.height_label.setText(translate('OpenLP.ScreensTab', 'Height'))
        self.screen_number_label.setText(translate('OpenLP.ScreensTab', '<strong>Screen 1</strong>'))
        self.identify_button.setText(translate('OpenLP.ScreensTab', 'Identify Screens'))

    def resizeEvent(self, event=None):
        """
        Override resizeEvent() to adjust the position of the identify_button.

        NB: Don't call SettingsTab's resizeEvent() because we're not using its widgets.
        """
        button_geometry = self.identify_button.geometry()
        frame_geometry = self.screen_frame.geometry()
        button_geometry.moveTop(frame_geometry.bottom() + 8)
        button_geometry.moveRight(frame_geometry.right())
        self.identify_button.setGeometry(button_geometry)
        QtWidgets.QWidget.resizeEvent(self, event)

    def show(self):
        """
        Override show just to do some initialisation
        """
        super(ScreensTab, self).show()
        if self.screen_frame_layout.count() > 2:
            self.screen_frame_layout.itemAt(1).widget().click()

    def _setup_spin_box(self, spin_box, mininum, maximum, value):
        """
        Set up the spin box
        """
        spin_box.setMinimum(mininum)
        spin_box.setMaximum(maximum)
        spin_box.setValue(value)

    def _save_screen(self, screen):
        """
        Save the details in the UI to the screen
        """
        if not screen:
            return
        screen.is_display = self.is_display_check_box.isChecked()
        if self.custom_geometry_button.isChecked():
            custom_geometry = QtCore.QRect()
            custom_geometry.setTop(self.top_spin_box.value())
            custom_geometry.setLeft(self.left_spin_box.value())
            custom_geometry.setWidth(self.width_spin_box.value())
            custom_geometry.setHeight(self.height_spin_box.value())
            screen.display_geometry = custom_geometry

    def load(self):
        """
        Load the settings to populate the tab
        """
        settings = Settings()
        settings.beginGroup(self.settings_section)
        # Remove all the existing items in the layout
        while self.screen_frame_layout.count() > 0:
            item = self.screen_frame_layout.takeAt(0)
            if item.widget() is not None:
                widget = item.widget()
                if widget in self.screen_button_group.buttons():
                    self.screen_button_group.removeButton(widget)
                widget.setParent(None)
                widget.deleteLater()
            del item
        # Add the existing screens into the frame
        self.screen_frame_layout.addStretch()
        for screen in self.screens:
            screen_button = ScreenButton(self.screen_frame, screen)
            screen_button.clicked.connect(self.on_screen_button_clicked)
            self.screen_frame_layout.addWidget(screen_button)
            self.screen_button_group.addButton(screen_button)
        self.screen_frame_layout.addStretch()

    def save(self):
        """
        Save the screen settings
        """
        self._save_screen(self.current_screen)
        settings = Settings()
        screen_settings = {}
        for screen in self.screens:
            screen_settings[screen.number] = screen.to_dict()
        settings.setValue('core/screens', screen_settings)
        # On save update the screens as well
        self.settings_form.register_post_process('config_screen_changed')

    @QtCore.pyqtSlot()
    def _on_identify_timer_shot(self):
        for label in self.identify_labels:
            label.hide()
            label.setParent(None)
            label.deleteLater()
        self.identify_labels = []

    def on_identify_button_clicked(self):
        """
        Display a widget on every screen for 5 seconds
        """
        for screen in self.screens:
            label = QtWidgets.QLabel(None)
            label.setAlignment(QtCore.Qt.AlignCenter)
            label.font().setBold(True)
            label.font().setPointSize(24)
            label.setText('<font size="24">Screen {number}</font>'.format(number=screen.number + 1))
            label.setStyleSheet('background-color: #0c0; color: #000; border: 5px solid #000;')
            label.setGeometry(QtCore.QRect(screen.geometry.x(), screen.geometry.y(), 200, 100))
            label.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Tool | QtCore.Qt.WindowStaysOnTopHint |
                                 QtCore.Qt.WindowDoesNotAcceptFocus)
            label.show()
            self.identify_labels.append(label)

        QtCore.QTimer.singleShot(3000, self._on_identify_timer_shot)

    def on_screen_button_clicked(self):
        """
        Respond to a screen button being clicked
        """
        screen = self.sender().screen
        if self.current_screen is not screen:
            self._save_screen(self.current_screen)
        self.screen_number_label.setText(str(screen))
        self.is_display_check_box.setChecked(screen.is_display)
        self.full_screen_radio_button.setChecked(screen.custom_geometry is None)
        self.custom_geometry_button.setChecked(screen.custom_geometry is not None)
        self._setup_spin_box(self.left_spin_box, screen.display_geometry.y(), screen.display_geometry.right(),
                             screen.display_geometry.x())
        self._setup_spin_box(self.top_spin_box, screen.display_geometry.y(), screen.display_geometry.bottom(),
                             screen.display_geometry.y())
        self._setup_spin_box(self.width_spin_box, 0, screen.display_geometry.width(), screen.display_geometry.width())
        self._setup_spin_box(self.height_spin_box, 0, screen.display_geometry.height(),
                             screen.display_geometry.height())
        self.current_screen = screen
