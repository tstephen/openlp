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
The service item edit dialog
"""
from PySide6 import QtCore, QtWidgets

from openlp.core.common.mixins import RegistryProperties
from openlp.core.common.registry import Registry
from openlp.core.ui.serviceitemeditdialog import Ui_ServiceItemEditDialog


class ServiceItemEditForm(QtWidgets.QDialog, Ui_ServiceItemEditDialog, RegistryProperties):
    """
    This is the form that is used to edit the verses of the song.
    """
    def __init__(self):
        """
        Constructor
        """
        super(ServiceItemEditForm, self).__init__(Registry().get('main_window'),
                                                  QtCore.Qt.WindowType.WindowSystemMenuHint |
                                                  QtCore.Qt.WindowType.WindowTitleHint |
                                                  QtCore.Qt.WindowType.WindowCloseButtonHint)
        self.setup_ui(self)
        self.item_list = []
        self.list_widget.currentRowChanged.connect(self.on_current_row_changed)

    def set_service_item(self, item):
        """
        Set the service item to be edited.
        """
        self.item = item
        self.item_list = []
        if self.item.is_image():
            self.data = True
            self.item_list.extend(self.item.slides)
        self.load_data()
        self.list_widget.setCurrentItem(self.list_widget.currentItem())

    def get_service_item(self):
        """
        Get the modified service item.
        """
        if self.data:
            # self.data is only true for images
            self.item.slides = []
            for item in self.item_list:
                thumb = item.get('thumbnail', None)
                file_hash = item.get('file_hash', None)
                self.item.add_from_image(item['path'], item['title'], thumb, file_hash)
        return self.item

    def load_data(self):
        """
        Loads the image list.
        """
        self.list_widget.clear()
        for frame in self.item_list:
            item_name = QtWidgets.QListWidgetItem(frame['title'])
            self.list_widget.addItem(item_name)

    def on_delete_button_clicked(self):
        """
        Delete the current row.
        """
        item = self.list_widget.currentItem()
        if not item:
            return
        row = self.list_widget.row(item)
        self.item_list.pop(row)
        self.load_data()
        if row == self.list_widget.count():
            row -= 1
        self.list_widget.setCurrentRow(row)

    def on_up_button_clicked(self):
        """
        Move the current row up in the list.
        """
        self.__move_item('up')

    def on_down_button_clicked(self):
        """
        Move the current row down in the list
        """
        self.__move_item('down')

    def __move_item(self, direction=''):
        """
        Move the current item.
        """
        if not direction:
            return
        item = self.list_widget.currentItem()
        if not item:
            return
        row = self.list_widget.row(item)
        temp = self.item_list[row]
        self.item_list.pop(row)
        if direction == 'up':
            row -= 1
        else:
            row += 1
        self.item_list.insert(row, temp)
        self.load_data()
        self.list_widget.setCurrentRow(row)

    def on_current_row_changed(self, row):
        """
        Called when the currentRow has changed.

        :param row: The row number (int).
        """
        # Disable all buttons, as no row is selected or only one image is left.
        if row == -1 or self.list_widget.count() == 1:
            self.down_button.setEnabled(False)
            self.up_button.setEnabled(False)
            self.delete_button.setEnabled(False)
        else:
            # Check if we are at the end of the list.
            if self.list_widget.count() == row + 1:
                self.down_button.setEnabled(False)
            else:
                self.down_button.setEnabled(True)
            # Check if we are at the beginning of the list.
            if row == 0:
                self.up_button.setEnabled(False)
            else:
                self.up_button.setEnabled(True)
            self.delete_button.setEnabled(True)
