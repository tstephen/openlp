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
from PySide6 import QtWidgets

from openlp.core.common.i18n import UiStrings, translate
from openlp.core.lib.ui import create_button, create_button_box
from openlp.core.ui.icons import UiIcons


class Ui_CustomEditDialog(object):
    def setup_ui(self, custom_edit_dialog):
        """
        Build the Edit Dialog UI
        :param custom_edit_dialog: The Dialog
        """
        custom_edit_dialog.setObjectName('custom_edit_dialog')
        custom_edit_dialog.setWindowIcon(UiIcons().main_icon)
        custom_edit_dialog.resize(450, 350)
        self.dialog_layout = QtWidgets.QVBoxLayout(custom_edit_dialog)
        self.dialog_layout.setObjectName('dialog_layout')
        self.title_layout = QtWidgets.QHBoxLayout()
        self.title_layout.setObjectName('title_layout')
        self.title_label = QtWidgets.QLabel(custom_edit_dialog)
        self.title_label.setObjectName('title_label')
        self.title_layout.addWidget(self.title_label)
        self.title_edit = QtWidgets.QLineEdit(custom_edit_dialog)
        self.title_label.setBuddy(self.title_edit)
        self.title_edit.setObjectName('title_edit')
        self.title_layout.addWidget(self.title_edit)
        self.dialog_layout.addLayout(self.title_layout)
        self.central_layout = QtWidgets.QHBoxLayout()
        self.central_layout.setObjectName('central_layout')
        self.slide_list_view = QtWidgets.QListWidget(custom_edit_dialog)
        self.slide_list_view.setAlternatingRowColors(True)
        self.slide_list_view.setObjectName('slide_list_view')
        self.central_layout.addWidget(self.slide_list_view)
        self.button_layout = QtWidgets.QVBoxLayout()
        self.button_layout.setObjectName('button_layout')
        self.add_button = QtWidgets.QPushButton(custom_edit_dialog)
        self.add_button.setObjectName('add_button')
        self.button_layout.addWidget(self.add_button)
        self.edit_button = QtWidgets.QPushButton(custom_edit_dialog)
        self.edit_button.setEnabled(False)
        self.edit_button.setObjectName('edit_button')
        self.button_layout.addWidget(self.edit_button)
        self.edit_all_button = QtWidgets.QPushButton(custom_edit_dialog)
        self.edit_all_button.setObjectName('edit_all_button')
        self.button_layout.addWidget(self.edit_all_button)
        self.delete_button = create_button(custom_edit_dialog, 'delete_button', role='delete',
                                           click=custom_edit_dialog.on_delete_button_clicked)
        self.delete_button.setEnabled(False)
        self.button_layout.addWidget(self.delete_button)
        self.button_layout.addStretch()
        self.up_button = create_button(custom_edit_dialog, 'up_button', role='up', enabled=False,
                                       click=custom_edit_dialog.on_up_button_clicked)
        self.down_button = create_button(custom_edit_dialog, 'down_button', role='down', enabled=False,
                                         click=custom_edit_dialog.on_down_button_clicked)
        self.button_layout.addWidget(self.up_button)
        self.button_layout.addWidget(self.down_button)
        self.central_layout.addLayout(self.button_layout)
        self.dialog_layout.addLayout(self.central_layout)
        self.bottom_form_layout = QtWidgets.QFormLayout()
        self.bottom_form_layout.setObjectName('bottom_form_layout')
        self.theme_label = QtWidgets.QLabel(custom_edit_dialog)
        self.theme_label.setObjectName('theme_label')
        self.theme_combo_box = QtWidgets.QComboBox(custom_edit_dialog)
        self.theme_combo_box.setSizeAdjustPolicy(QtWidgets.QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.theme_combo_box.setObjectName('theme_combo_box')
        self.theme_label.setBuddy(self.theme_combo_box)
        self.bottom_form_layout.addRow(self.theme_label, self.theme_combo_box)
        self.credit_label = QtWidgets.QLabel(custom_edit_dialog)
        self.credit_label.setObjectName('credit_label')
        self.credit_edit = QtWidgets.QLineEdit(custom_edit_dialog)
        self.credit_edit.setObjectName('credit_edit')
        self.credit_label.setBuddy(self.credit_edit)
        self.bottom_form_layout.addRow(self.credit_label, self.credit_edit)
        self.dialog_layout.addLayout(self.bottom_form_layout)
        self.preview_button = QtWidgets.QPushButton()
        self.button_box = create_button_box(custom_edit_dialog, 'button_box', ['cancel', 'save', 'help'],
                                            [self.preview_button])
        self.save_button = self.button_box.button(QtWidgets.QDialogButtonBox.StandardButton.Save)
        self.dialog_layout.addWidget(self.button_box)
        self.retranslate_ui(custom_edit_dialog)

    def retranslate_ui(self, custom_edit_dialog):
        custom_edit_dialog.setWindowTitle(translate('CustomPlugin.EditCustomForm', 'Edit Custom Slides'))
        self.title_label.setText(translate('CustomPlugin.EditCustomForm', '&Title:'))
        self.add_button.setText(UiStrings().Add)
        self.add_button.setToolTip(translate('CustomPlugin.EditCustomForm', 'Add a new slide at bottom.'))
        self.edit_button.setText(UiStrings().Edit)
        self.edit_button.setToolTip(translate('CustomPlugin.EditCustomForm', 'Edit the selected slide.'))
        self.edit_all_button.setText(translate('CustomPlugin.EditCustomForm', 'Ed&it All'))
        self.edit_all_button.setToolTip(translate('CustomPlugin.EditCustomForm', 'Edit all the slides at once.'))
        self.theme_label.setText(translate('CustomPlugin.EditCustomForm', 'The&me:'))
        self.credit_label.setText(translate('CustomPlugin.EditCustomForm', '&Credits:'))
        self.preview_button.setText(UiStrings().SaveAndPreview)
        self.save_button.setText(UiStrings().SaveAndClose)
