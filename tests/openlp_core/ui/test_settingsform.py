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
Package to test the openlp.core.ui.settingsform package.
"""
from unittest.mock import MagicMock, patch

from PySide6 import QtCore, QtWidgets, QtTest

from openlp.core.ui.settingsform import SettingsForm


def test_insert_tab_visible(registry, mock_settings):
    """
    Test that the insert_tab() method works correctly when a visible tab is inserted
    """
    # GIVEN: A mocked tab and a Settings Form
    settings_form = SettingsForm(None)
    general_tab = MagicMock()
    general_tab.tab_title = 'mock'
    general_tab.tab_title_visible = 'Mock'
    general_tab.icon_path = ':/icon/openlp-logo.svg'

    # WHEN: We insert the general tab
    with patch.object(settings_form.stacked_layout, 'addWidget') as mocked_add_widget, \
            patch.object(settings_form.setting_list_widget, 'addItem') as mocked_add_item:
        settings_form.insert_tab(general_tab, is_visible=True)

        # THEN: The general tab should have been inserted into the stacked layout and an item inserted into the list
        mocked_add_widget.assert_called_with(general_tab)
        assert 1 == mocked_add_item.call_count, 'addItem should have been called'


def test_insert_tab_not_visible(registry, mock_settings):
    """
    Test that the insert_tab() method works correctly when a tab that should not be visible is inserted
    """
    # GIVEN: A general tab and a Settings Form
    settings_form = SettingsForm(None)
    general_tab = MagicMock()
    general_tab.tab_title = 'mock'

    # WHEN: We insert the general tab
    with patch.object(settings_form.stacked_layout, 'addWidget') as mocked_add_widget, \
            patch.object(settings_form.setting_list_widget, 'addItem') as mocked_add_item:
        settings_form.insert_tab(general_tab, is_visible=False)

        # THEN: The general tab should have been inserted, but no list item should have been inserted into the list
        mocked_add_widget.assert_called_with(general_tab)
        assert 0 == mocked_add_item.call_count, 'addItem should not have been called'


def test_accept_with_inactive_plugins(registry, mock_settings):
    """
    Test that the accept() method works correctly when some of the plugins are inactive
    """
    # GIVEN: A visible general tab and an invisible theme tab in a Settings Form
    settings_form = SettingsForm(None)
    general_tab = QtWidgets.QWidget(None)
    general_tab.tab_title = 'mock-general'
    general_tab.tab_title_visible = 'Mock General'
    general_tab.icon_path = ':/icon/openlp-logo.svg'
    mocked_general_save = MagicMock()
    general_tab.save = mocked_general_save
    mocked_general_load = MagicMock()
    general_tab.load = mocked_general_load
    settings_form.insert_tab(general_tab, is_visible=True)
    themes_tab = QtWidgets.QWidget(None)
    themes_tab.tab_title = 'mock-themes'
    themes_tab.tab_title_visible = 'Mock Themes'
    themes_tab.icon_path = ':/icon/openlp-logo.svg'
    mocked_theme_save = MagicMock()
    themes_tab.save = mocked_theme_save
    mocked_theme_load = MagicMock()
    themes_tab.load = mocked_theme_load
    settings_form.insert_tab(themes_tab, is_visible=False)

    # WHEN: The accept() method is called
    settings_form.accept()

    # THEN: The general tab's save() method should have been called, but not the themes tab
    mocked_general_save.assert_called_with()
    assert 0 == mocked_theme_save.call_count, 'The Themes tab\'s save() should not have been called'


def test_list_item_changed_invalid_item(registry, mock_settings):
    """
    Test that the list_item_changed() slot handles a non-existent item
    """
    # GIVEN: A mocked tab inserted into a Settings Form
    settings_form = SettingsForm(None)
    general_tab = QtWidgets.QWidget(None)
    general_tab.tab_title = 'mock'
    general_tab.tab_title_visible = 'Mock'
    general_tab.icon_path = ':/icon/openlp-logo.svg'
    mocked_general_load = MagicMock()
    general_tab.load = mocked_general_load
    settings_form.insert_tab(general_tab, is_visible=True)

    with patch.object(settings_form.stacked_layout, 'count') as mocked_count:
        # WHEN: The list_item_changed() slot is called with an invalid item index
        settings_form.list_item_changed(100)

        # THEN: The rest of the method should not have been called
        assert 0 == mocked_count.call_count, 'The count method of the stacked layout should not be called'


def test_reject_with_inactive_items(registry, mock_settings):
    """
    Test that the reject() method works correctly when some of the plugins are inactive
    """
    # GIVEN: A visible general tab and an invisible theme tab in a Settings Form
    settings_form = SettingsForm(None)
    general_tab = QtWidgets.QWidget(None)
    general_tab.tab_title = 'mock-general'
    general_tab.tab_title_visible = 'Mock General'
    general_tab.icon_path = ':/icon/openlp-logo.svg'
    mocked_general_cancel = MagicMock()
    general_tab.cancel = mocked_general_cancel
    mocked_general_load = MagicMock()
    general_tab.load = mocked_general_load
    settings_form.insert_tab(general_tab, is_visible=True)
    themes_tab = QtWidgets.QWidget(None)
    themes_tab.tab_title = 'mock-themes'
    themes_tab.tab_title_visible = 'Mock Themes'
    themes_tab.icon_path = ':/icon/openlp-logo.svg'
    mocked_theme_cancel = MagicMock()
    themes_tab.cancel = mocked_theme_cancel
    settings_form.insert_tab(themes_tab, is_visible=False)

    # WHEN: The reject() method is called
    settings_form.reject()

    # THEN: The general tab's cancel() method should have been called, but not the themes tab
    mocked_general_cancel.assert_called_with()
    assert 0 == mocked_theme_cancel.call_count, 'The Themes tab\'s cancel() should not have been called'


def test_register_post_process(registry, mock_settings):
    """
    Test that the register_post_process() method works correctly
    """
    # GIVEN: A settings form instance
    settings_form = SettingsForm(None)
    fake_function = MagicMock()

    # WHEN: register_post_process() is called
    settings_form.register_post_process(fake_function)

    # THEN: The fake function should be in the settings form's list
    assert fake_function in settings_form.processes


@patch.object(SettingsForm, 'provide_help')
def test_help(mocked_help, mock_settings):
    """
    Test the help button
    """
    # GIVEN: An initialised Settings form and a patched help function
    settings_form = SettingsForm(None)

    # WHEN: The Help button is clicked
    QtTest.QTest.mouseClick(settings_form.button_box.button(QtWidgets.QDialogButtonBox.StandardButton.Help),
                            QtCore.Qt.MouseButton.LeftButton)

    # THEN: The Help function should be called
    mocked_help.assert_called_once()
