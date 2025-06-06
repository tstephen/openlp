# -*- coding: utf-8 -*-

##########################################################################
# OpenLP - Open Source Lyrics Projection                                 #
# ---------------------------------------------------------------------- #
# Copyright (c) 2008 OpenLP Developers                                   #
# ---------------------------------------------------------------------- #
# This program is free software: you can redistribute it and/or modify   #
# it under the terms of the GNU General Public License as published by   #
# the Free Software Foundation, either version 3 of the License, or      #
# (at your option) any later version.                                    #
#                                                                        #
# This program is distributed in the hope that it will be useful,        #
# but WITHOUT ANY WARRANTY; without even the implied warranty of         #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
# GNU General Public License for more details.                           #
#                                                                        #
# You should have received a copy of the GNU General Public License      #
# along with this program.  If not, see <https://www.gnu.org/licenses/>. #
##########################################################################
"""
Package to test the openlp.plugins.songusage.forms.songusagedeleteform package.
"""
from unittest.mock import MagicMock, patch

from PySide6 import QtWidgets, QtTest, QtCore

from openlp.plugins.songusage.forms.songusagedeleteform import SongUsageDeleteForm


@patch.object(SongUsageDeleteForm, 'provide_help')
def test_help(mocked_help, settings):
    """
    Test the help button
    """
    # GIVEN: A songusage delete form and a patched help function
    main_window = QtWidgets.QMainWindow()
    delete_form = SongUsageDeleteForm(MagicMock(), main_window)

    # WHEN: The Help button is clicked
    QtTest.QTest.mouseClick(delete_form.button_box.button(
        QtWidgets.QDialogButtonBox.StandardButton.Help), QtCore.Qt.MouseButton.LeftButton)

    # THEN: The Help function should be called
    mocked_help.assert_called_once()
