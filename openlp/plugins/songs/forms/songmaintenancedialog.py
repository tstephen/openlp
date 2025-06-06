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

from PySide6 import QtCore, QtWidgets

from openlp.core.common.i18n import UiStrings
from openlp.core.lib.ui import create_button_box
from openlp.core.ui.icons import UiIcons
from openlp.plugins.songs.lib.ui import SongStrings


class Ui_SongMaintenanceDialog(object):
    """
    The user interface for the song maintenance dialog
    """
    def setup_ui(self, song_maintenance_dialog):
        """
        Set up the user interface for the song maintenance dialog
        """
        song_maintenance_dialog.setObjectName('song_maintenance_dialog')
        song_maintenance_dialog.setWindowIcon(UiIcons().main_icon)
        song_maintenance_dialog.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
        song_maintenance_dialog.resize(600, 600)
        self.dialog_layout = QtWidgets.QGridLayout(song_maintenance_dialog)
        self.dialog_layout.setObjectName('dialog_layout')
        self.type_list_widget = QtWidgets.QListWidget(song_maintenance_dialog)
        self.type_list_widget.setIconSize(QtCore.QSize(32, 32))
        self.type_list_widget.setUniformItemSizes(True)
        self.type_list_widget.setObjectName('type_list_widget')
        self.authors_list_item = QtWidgets.QListWidgetItem(self.type_list_widget)
        self.authors_list_item.setIcon(UiIcons().usermo)
        self.topics_list_item = QtWidgets.QListWidgetItem(self.type_list_widget)
        self.topics_list_item.setIcon(UiIcons().light_bulb)
        self.books_list_item = QtWidgets.QListWidgetItem(self.type_list_widget)
        self.books_list_item.setIcon(UiIcons().book)
        self.dialog_layout.addWidget(self.type_list_widget, 0, 0)
        self.stacked_layout = QtWidgets.QStackedLayout()
        self.stacked_layout.setObjectName('stacked_layout')
        # authors page
        self.authors_page = QtWidgets.QWidget(song_maintenance_dialog)
        self.authors_page.setObjectName('authors_page')
        self.authors_layout = QtWidgets.QVBoxLayout(self.authors_page)
        self.authors_layout.setObjectName('authors_layout')
        self.authors_list_widget = QtWidgets.QListWidget(self.authors_page)
        self.authors_list_widget.setObjectName('authors_list_widget')
        self.authors_layout.addWidget(self.authors_list_widget)
        self.authors_buttons_layout = QtWidgets.QHBoxLayout()
        self.authors_buttons_layout.setObjectName('authors_buttons_layout')
        self.authors_buttons_layout.addStretch()
        self.add_author_button = QtWidgets.QPushButton(self.authors_page)
        self.add_author_button.setIcon(UiIcons().add)
        self.add_author_button.setObjectName('add_author_button')
        self.authors_buttons_layout.addWidget(self.add_author_button)
        self.edit_author_button = QtWidgets.QPushButton(self.authors_page)
        self.edit_author_button.setIcon(UiIcons().edit)
        self.edit_author_button.setObjectName('edit_author_button')
        self.authors_buttons_layout.addWidget(self.edit_author_button)
        self.delete_author_button = QtWidgets.QPushButton(self.authors_page)
        self.delete_author_button.setIcon(UiIcons().delete)
        self.delete_author_button.setObjectName('delete_author_button')
        self.authors_buttons_layout.addWidget(self.delete_author_button)
        self.authors_layout.addLayout(self.authors_buttons_layout)
        self.stacked_layout.addWidget(self.authors_page)
        # topics page
        self.topics_page = QtWidgets.QWidget(song_maintenance_dialog)
        self.topics_page.setObjectName('topics_page')
        self.topics_layout = QtWidgets.QVBoxLayout(self.topics_page)
        self.topics_layout.setObjectName('topics_layout')
        self.topics_list_widget = QtWidgets.QListWidget(self.topics_page)
        self.topics_list_widget.setObjectName('topics_list_widget')
        self.topics_layout.addWidget(self.topics_list_widget)
        self.topics_buttons_layout = QtWidgets.QHBoxLayout()
        self.topics_buttons_layout.setObjectName('topicsButtonLayout')
        self.topics_buttons_layout.addStretch()
        self.add_topic_button = QtWidgets.QPushButton(self.topics_page)
        self.add_topic_button.setIcon(UiIcons().add)
        self.add_topic_button.setObjectName('add_topic_button')
        self.topics_buttons_layout.addWidget(self.add_topic_button)
        self.edit_topic_button = QtWidgets.QPushButton(self.topics_page)
        self.edit_topic_button.setIcon(UiIcons().edit)
        self.edit_topic_button.setObjectName('edit_topic_button')
        self.topics_buttons_layout.addWidget(self.edit_topic_button)
        self.delete_topic_button = QtWidgets.QPushButton(self.topics_page)
        self.delete_topic_button.setIcon(UiIcons().delete)
        self.delete_topic_button.setObjectName('delete_topic_button')
        self.topics_buttons_layout.addWidget(self.delete_topic_button)
        self.topics_layout.addLayout(self.topics_buttons_layout)
        self.stacked_layout.addWidget(self.topics_page)
        # song books page
        self.books_page = QtWidgets.QWidget(song_maintenance_dialog)
        self.books_page.setObjectName('books_page')
        self.books_layout = QtWidgets.QVBoxLayout(self.books_page)
        self.books_layout.setObjectName('books_layout')
        self.song_books_list_widget = QtWidgets.QListWidget(self.books_page)
        self.song_books_list_widget.setObjectName('song_books_list_widget')
        self.books_layout.addWidget(self.song_books_list_widget)
        self.books_buttons_layout = QtWidgets.QHBoxLayout()
        self.books_buttons_layout.setObjectName('booksButtonLayout')
        self.books_buttons_layout.addStretch()
        self.add_book_button = QtWidgets.QPushButton(self.books_page)
        self.add_book_button.setIcon(UiIcons().add)
        self.add_book_button.setObjectName('add_book_button')
        self.books_buttons_layout.addWidget(self.add_book_button)
        self.edit_book_button = QtWidgets.QPushButton(self.books_page)
        self.edit_book_button.setIcon(UiIcons().edit)
        self.edit_book_button.setObjectName('edit_book_button')
        self.books_buttons_layout.addWidget(self.edit_book_button)
        self.delete_book_button = QtWidgets.QPushButton(self.books_page)
        self.delete_book_button.setIcon(UiIcons().delete)
        self.delete_book_button.setObjectName('delete_book_button')
        self.books_buttons_layout.addWidget(self.delete_book_button)
        self.books_layout.addLayout(self.books_buttons_layout)
        self.stacked_layout.addWidget(self.books_page)
        #
        self.dialog_layout.addLayout(self.stacked_layout, 0, 1)
        self.button_box = create_button_box(song_maintenance_dialog, 'button_box', ['close'])
        self.dialog_layout.addWidget(self.button_box, 1, 0, 1, 2)
        self.retranslate_ui(song_maintenance_dialog)
        self.stacked_layout.setCurrentIndex(0)
        self.type_list_widget.currentRowChanged.connect(self.stacked_layout.setCurrentIndex)

    def retranslate_ui(self, song_maintenance_dialog):
        """
        Translate the UI on the fly.
        """
        song_maintenance_dialog.setWindowTitle(SongStrings().SongMaintenance)
        self.authors_list_item.setText(SongStrings().Authors)
        self.topics_list_item.setText(SongStrings().Topics)
        self.books_list_item.setText(SongStrings().SongBooks)
        self.add_author_button.setText(UiStrings().Add)
        self.edit_author_button.setText(UiStrings().Edit)
        self.delete_author_button.setText(UiStrings().Delete)
        self.add_topic_button.setText(UiStrings().Add)
        self.edit_topic_button.setText(UiStrings().Edit)
        self.delete_topic_button.setText(UiStrings().Delete)
        self.add_book_button.setText(UiStrings().Add)
        self.edit_book_button.setText(UiStrings().Edit)
        self.delete_book_button.setText(UiStrings().Delete)
        type_list_width = max(self.fontMetrics().width(SongStrings().Authors),
                              self.fontMetrics().width(SongStrings().Topics),
                              self.fontMetrics().width(SongStrings().SongBooks))
        self.type_list_widget.setFixedWidth(type_list_width + self.type_list_widget.iconSize().width() + 32)
