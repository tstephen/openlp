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
from PyQt5 import QtWidgets

from openlp.core.common.i18n import translate
from openlp.core.common.settings import Settings
from openlp.core.display.screens import ScreenList
from openlp.core.lib.settingstab import SettingsTab
from openlp.core.common.registry import Registry
from openlp.core.ui.icons import UiIcons
from openlp.core.widgets.widgets import ScreenSelectionWidget


class ScreensTab(SettingsTab):
    """
    ScreensTab is the screen settings tab in the configuration dialog
    """
    def __init__(self, parent):
        """
        Initialise the screen settings tab
        """
        self.icon_path = UiIcons().settings
        screens_translated = translate('OpenLP.ScreensTab', 'Screens')
        super(ScreensTab, self).__init__(parent, 'Screens', screens_translated)
        self.settings_section = 'core'

    def setup_ui(self):
        """
        Set up the user interface elements
        """
        self.setObjectName('self')
        self.tab_layout = QtWidgets.QVBoxLayout(self)
        self.tab_layout.setObjectName('tab_layout')

        self.screen_selection_widget = ScreenSelectionWidget(self, ScreenList())
        self.tab_layout.addWidget(self.screen_selection_widget)

        Registry().register_function('config_screen_changed', self.screen_selection_widget.load)

    def retranslate_ui(self):
        self.setWindowTitle(translate('self', 'self'))  # TODO: ???

    def load(self):
        """
        Load the settings to populate the tab
        """
        settings = Settings()
        settings.beginGroup(self.settings_section)
        self.screen_selection_widget.load()

    def resizeEvent(self, event=None):
        """
        Override resizeEvent() to adjust the position of the identify_button.

        NB: Don't call SettingsTab's resizeEvent() because we're not using its widgets.
        """
        QtWidgets.QWidget.resizeEvent(self, event)

    def save(self):
        self.screen_selection_widget.save()
        self.settings_form.register_post_process('config_screen_changed')
