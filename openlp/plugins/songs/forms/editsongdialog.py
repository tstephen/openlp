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

from PySide6 import QtCore, QtGui, QtWidgets

from openlp.core.common.i18n import UiStrings, translate
from openlp.core.lib.ui import create_button, create_button_box
from openlp.core.ui import SingleColumnTableWidget
from openlp.core.ui.icons import UiIcons
from openlp.plugins.songs.lib.ui import SongStrings


class Ui_EditSongDialog(object):
    """
    The :class:`~openlp.plugins.songs.forms.editsongdialog.Ui_EditSongDialog` class defines the user interface for the
    EditSongForm dialog.
    """
    def setup_ui(self, edit_song_dialog):
        edit_song_dialog.setObjectName('edit_song_dialog')
        edit_song_dialog.setWindowIcon(UiIcons().main_icon)
        edit_song_dialog.resize(900, 600)
        edit_song_dialog.setModal(True)
        self.dialog_layout = QtWidgets.QVBoxLayout(edit_song_dialog)
        self.dialog_layout.setSpacing(8)
        self.dialog_layout.setContentsMargins(8, 8, 8, 8)
        self.dialog_layout.setObjectName('dialog_layout')
        self.song_tab_widget = QtWidgets.QTabWidget(edit_song_dialog)
        self.song_tab_widget.setObjectName('song_tab_widget')
        # lyrics tab
        self.lyrics_tab = QtWidgets.QWidget()
        self.lyrics_tab.setObjectName('lyrics_tab')
        self.lyrics_tab_layout = QtWidgets.QGridLayout(self.lyrics_tab)
        self.lyrics_tab_layout.setObjectName('lyrics_tab_layout')
        self.title_label = QtWidgets.QLabel(self.lyrics_tab)
        self.title_label.setObjectName('title_label')
        self.lyrics_tab_layout.addWidget(self.title_label, 0, 0)
        self.title_edit = QtWidgets.QLineEdit(self.lyrics_tab)
        self.title_edit.setObjectName('title_edit')
        self.title_label.setBuddy(self.title_edit)
        self.lyrics_tab_layout.addWidget(self.title_edit, 0, 1, 1, 2)
        self.alternative_title_label = QtWidgets.QLabel(self.lyrics_tab)
        self.alternative_title_label.setObjectName('alternative_title_label')
        self.lyrics_tab_layout.addWidget(self.alternative_title_label, 1, 0)
        self.alternative_edit = QtWidgets.QLineEdit(self.lyrics_tab)
        self.alternative_edit.setObjectName('alternative_edit')
        self.alternative_title_label.setBuddy(self.alternative_edit)
        self.lyrics_tab_layout.addWidget(self.alternative_edit, 1, 1, 1, 2)
        self.lyrics_label = QtWidgets.QLabel(self.lyrics_tab)
        self.lyrics_label.setFixedHeight(self.title_edit.sizeHint().height())
        self.lyrics_label.setObjectName('lyrics_label')
        self.lyrics_tab_layout.addWidget(self.lyrics_label, 2, 0, QtCore.Qt.AlignmentFlag.AlignTop)
        self.verse_list_widget = SingleColumnTableWidget(self.lyrics_tab)
        self.verse_list_widget.setAlternatingRowColors(True)
        self.verse_list_widget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.verse_list_widget.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.verse_list_widget.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.verse_list_widget.setObjectName('verse_list_widget')
        self.lyrics_label.setBuddy(self.verse_list_widget)
        self.lyrics_tab_layout.addWidget(self.verse_list_widget, 2, 1)
        self.verse_order_label = QtWidgets.QLabel(self.lyrics_tab)
        self.verse_order_label.setObjectName('verse_order_label')
        self.lyrics_tab_layout.addWidget(self.verse_order_label, 3, 0)
        self.verse_order_edit = QtWidgets.QLineEdit(self.lyrics_tab)
        self.verse_order_edit.setObjectName('verse_order_edit')
        self.verse_order_label.setBuddy(self.verse_order_edit)
        self.lyrics_tab_layout.addWidget(self.verse_order_edit, 3, 1, 1, 2)
        self.verse_buttons_layout = QtWidgets.QVBoxLayout()
        self.verse_buttons_layout.setObjectName('verse_buttons_layout')
        self.verse_add_button = QtWidgets.QPushButton(self.lyrics_tab)
        self.verse_add_button.setObjectName('verse_add_button')
        self.verse_buttons_layout.addWidget(self.verse_add_button)
        self.verse_edit_button = QtWidgets.QPushButton(self.lyrics_tab)
        self.verse_edit_button.setObjectName('verse_edit_button')
        self.verse_buttons_layout.addWidget(self.verse_edit_button)
        self.verse_edit_all_button = QtWidgets.QPushButton(self.lyrics_tab)
        self.verse_edit_all_button.setObjectName('verse_edit_all_button')
        self.verse_buttons_layout.addWidget(self.verse_edit_all_button)
        self.verse_delete_button = QtWidgets.QPushButton(self.lyrics_tab)
        self.verse_delete_button.setObjectName('verse_delete_button')
        self.verse_buttons_layout.addWidget(self.verse_delete_button)
        self.verse_buttons_layout.addStretch()
        self.lyrics_tab_layout.addLayout(self.verse_buttons_layout, 2, 2)
        self.song_tab_widget.addTab(self.lyrics_tab, '')
        # authors tab
        self.authors_tab = QtWidgets.QWidget()
        self.authors_tab.setObjectName('authors_tab')
        self.authors_tab_layout = QtWidgets.QHBoxLayout(self.authors_tab)
        self.authors_tab_layout.setObjectName('authors_tab_layout')
        self.authors_left_layout = QtWidgets.QVBoxLayout()
        self.authors_left_layout.setObjectName('authors_left_layout')
        self.authors_group_box = QtWidgets.QGroupBox(self.authors_tab)
        self.authors_group_box.setObjectName('authors_group_box')
        self.authors_layout = QtWidgets.QVBoxLayout(self.authors_group_box)
        self.authors_layout.setObjectName('authors_layout')
        self.author_add_layout = QtWidgets.QVBoxLayout()
        self.author_add_layout.setObjectName('author_add_layout')
        self.author_type_layout = QtWidgets.QHBoxLayout()
        self.author_type_layout.setObjectName('author_type_layout')
        self.authors_combo_box = create_combo_box(self.authors_group_box, 'authors_combo_box')
        self.author_add_layout.addWidget(self.authors_combo_box)
        self.author_types_combo_box = create_combo_box(self.authors_group_box, 'author_types_combo_box', editable=False)
        self.author_type_layout.addWidget(self.author_types_combo_box)
        self.author_add_button = QtWidgets.QPushButton(self.authors_group_box)
        self.author_add_button.setObjectName('author_add_button')
        self.author_type_layout.addWidget(self.author_add_button)
        self.author_add_layout.addLayout(self.author_type_layout)
        self.authors_layout.addLayout(self.author_add_layout)
        self.authors_list_view = QtWidgets.QListWidget(self.authors_group_box)
        self.authors_list_view.setAlternatingRowColors(True)
        self.authors_list_view.setObjectName('authors_list_view')
        self.authors_layout.addWidget(self.authors_list_view)
        self.author_remove_layout = QtWidgets.QHBoxLayout()
        self.author_remove_layout.setObjectName('author_remove_layout')
        self.author_remove_layout.addStretch()
        self.author_edit_button = QtWidgets.QPushButton(self.authors_group_box)
        self.author_edit_button.setObjectName('author_edit_button')
        self.author_remove_layout.addWidget(self.author_edit_button)
        self.author_remove_button = QtWidgets.QPushButton(self.authors_group_box)
        self.author_remove_button.setObjectName('author_remove_button')
        self.author_remove_layout.addWidget(self.author_remove_button)
        self.authors_layout.addLayout(self.author_remove_layout)
        self.authors_left_layout.addWidget(self.authors_group_box)
        self.maintenance_layout = QtWidgets.QHBoxLayout()
        self.maintenance_layout.setObjectName('maintenance_layout')
        self.maintenance_button = QtWidgets.QPushButton(self.authors_tab)
        self.maintenance_button.setObjectName('maintenance_button')
        self.maintenance_layout.addWidget(self.maintenance_button)
        self.maintenance_layout.addStretch()
        self.authors_left_layout.addLayout(self.maintenance_layout)
        self.authors_tab_layout.addLayout(self.authors_left_layout)
        self.authors_right_layout = QtWidgets.QVBoxLayout()
        self.authors_right_layout.setObjectName('authors_right_layout')
        self.topics_group_box = QtWidgets.QGroupBox(self.authors_tab)
        self.topics_group_box.setObjectName('topics_group_box')
        self.topics_layout = QtWidgets.QVBoxLayout(self.topics_group_box)
        self.topics_layout.setObjectName('topics_layout')
        self.topic_add_layout = QtWidgets.QHBoxLayout()
        self.topic_add_layout.setObjectName('topic_add_layout')
        self.topics_combo_box = create_combo_box(self.topics_group_box, 'topics_combo_box')
        self.topic_add_layout.addWidget(self.topics_combo_box)
        self.topic_add_button = QtWidgets.QPushButton(self.topics_group_box)
        self.topic_add_button.setObjectName('topic_add_button')
        self.topic_add_layout.addWidget(self.topic_add_button)
        self.topics_layout.addLayout(self.topic_add_layout)
        self.topics_list_view = QtWidgets.QListWidget(self.topics_group_box)
        self.topics_list_view.setAlternatingRowColors(True)
        self.topics_list_view.setObjectName('topics_list_view')
        self.topics_layout.addWidget(self.topics_list_view)
        self.topic_remove_layout = QtWidgets.QHBoxLayout()
        self.topic_remove_layout.setObjectName('topic_remove_layout')
        self.topic_remove_layout.addStretch()
        self.topic_remove_button = QtWidgets.QPushButton(self.topics_group_box)
        self.topic_remove_button.setObjectName('topic_remove_button')
        self.topic_remove_layout.addWidget(self.topic_remove_button)
        self.topics_layout.addLayout(self.topic_remove_layout)
        self.authors_right_layout.addWidget(self.topics_group_box)
        self.songbook_group_box = QtWidgets.QGroupBox(self.authors_tab)
        self.songbook_group_box.setObjectName('songbook_group_box')
        self.songbooks_layout = QtWidgets.QVBoxLayout(self.songbook_group_box)
        self.songbooks_layout.setObjectName('songbooks_layout')
        self.songbook_add_layout = QtWidgets.QHBoxLayout()
        self.songbook_add_layout.setObjectName('songbook_add_layout')
        self.songbooks_combo_box = create_combo_box(self.songbook_group_box, 'songbooks_combo_box')
        self.songbook_add_layout.addWidget(self.songbooks_combo_box)
        self.songbook_entry_edit = QtWidgets.QLineEdit(self.songbook_group_box)
        self.songbook_entry_edit.setMaximumWidth(100)
        self.songbook_add_layout.addWidget(self.songbook_entry_edit)
        self.songbook_add_button = QtWidgets.QPushButton(self.songbook_group_box)
        self.songbook_add_button.setObjectName('songbook_add_button')
        self.songbook_add_layout.addWidget(self.songbook_add_button)
        self.songbooks_layout.addLayout(self.songbook_add_layout)
        self.songbooks_list_view = QtWidgets.QListWidget(self.songbook_group_box)
        self.songbooks_list_view.setAlternatingRowColors(True)
        self.songbooks_list_view.setObjectName('songbooks_list_view')
        self.songbooks_layout.addWidget(self.songbooks_list_view)
        self.songbook_remove_layout = QtWidgets.QHBoxLayout()
        self.songbook_remove_layout.setObjectName('songbook_remove_layout')
        self.songbook_remove_layout.addStretch()
        self.songbook_remove_button = QtWidgets.QPushButton(self.songbook_group_box)
        self.songbook_remove_button.setObjectName('songbook_remove_button')
        self.songbook_remove_layout.addWidget(self.songbook_remove_button)
        self.songbooks_layout.addLayout(self.songbook_remove_layout)
        self.authors_right_layout.addWidget(self.songbook_group_box)
        self.authors_tab_layout.addLayout(self.authors_right_layout)
        self.song_tab_widget.addTab(self.authors_tab, '')
        # theme tab
        self.theme_tab = QtWidgets.QWidget()
        self.theme_tab.setObjectName('theme_tab')
        self.theme_tab_layout = QtWidgets.QHBoxLayout(self.theme_tab)
        self.theme_tab_layout.setObjectName('theme_tab_layout')
        self.theme_left_layout = QtWidgets.QVBoxLayout()
        self.theme_left_layout.setObjectName('theme_left_layout')
        self.theme_group_box = QtWidgets.QGroupBox(self.theme_tab)
        self.theme_group_box.setObjectName('theme_group_box')
        self.theme_layout = QtWidgets.QHBoxLayout(self.theme_group_box)
        self.theme_layout.setObjectName('theme_layout')
        self.theme_combo_box = create_combo_box(self.theme_group_box, 'theme_combo_box')
        self.theme_layout.addWidget(self.theme_combo_box)
        self.theme_add_button = QtWidgets.QPushButton(self.theme_group_box)
        self.theme_add_button.setObjectName('theme_add_button')
        self.theme_layout.addWidget(self.theme_add_button)
        self.theme_left_layout.addWidget(self.theme_group_box)
        self.rights_group_box = QtWidgets.QGroupBox(self.theme_tab)
        self.rights_group_box.setObjectName('rights_group_box')
        self.rights_layout = QtWidgets.QVBoxLayout(self.rights_group_box)
        self.rights_layout.setObjectName('rights_layout')
        self.copyright_layout = QtWidgets.QHBoxLayout()
        self.copyright_layout.setObjectName('copyright_layout')
        self.copyright_edit = QtWidgets.QLineEdit(self.rights_group_box)
        self.copyright_edit.setObjectName('copyright_edit')
        self.copyright_layout.addWidget(self.copyright_edit)
        self.copyright_insert_button = QtWidgets.QToolButton(self.rights_group_box)
        self.copyright_insert_button.setObjectName('copyright_insert_button')
        self.copyright_layout.addWidget(self.copyright_insert_button)
        self.rights_layout.addLayout(self.copyright_layout)
        self.ccli_layout = QtWidgets.QHBoxLayout()
        self.ccli_layout.setObjectName('ccli_layout')
        self.ccli_label = QtWidgets.QLabel(self.rights_group_box)
        self.ccli_label.setObjectName('ccli_label')
        self.ccli_layout.addWidget(self.ccli_label)
        self.ccli_number_edit = QtWidgets.QLineEdit(self.rights_group_box)
        self.ccli_number_edit.setValidator(QtGui.QIntValidator())
        self.ccli_number_edit.setObjectName('ccli_number_edit')
        self.ccli_layout.addWidget(self.ccli_number_edit)
        self.rights_layout.addLayout(self.ccli_layout)
        self.theme_left_layout.addWidget(self.rights_group_box)
        self.theme_left_layout.addStretch()
        self.theme_tab_layout.addLayout(self.theme_left_layout)
        self.comments_group_box = QtWidgets.QGroupBox(self.theme_tab)
        self.comments_group_box.setObjectName('comments_group_box')
        self.comments_layout = QtWidgets.QVBoxLayout(self.comments_group_box)
        self.comments_layout.setObjectName('comments_layout')
        self.comments_edit = QtWidgets.QTextEdit(self.comments_group_box)
        self.comments_edit.setObjectName('comments_edit')
        self.comments_layout.addWidget(self.comments_edit)
        self.theme_tab_layout.addWidget(self.comments_group_box)
        self.song_tab_widget.addTab(self.theme_tab, '')
        # audio tab
        self.audio_tab = QtWidgets.QWidget()
        self.audio_tab.setObjectName('audio_tab')
        self.audio_layout = QtWidgets.QHBoxLayout(self.audio_tab)
        self.audio_layout.setObjectName('audio_layout')
        self.audio_list_widget = QtWidgets.QListWidget(self.audio_tab)
        self.audio_list_widget.setObjectName('audio_list_widget')
        self.audio_layout.addWidget(self.audio_list_widget)
        self.audio_buttons_layout = QtWidgets.QVBoxLayout()
        self.audio_buttons_layout.setObjectName('audio_buttons_layout')
        self.from_file_button = QtWidgets.QPushButton(self.audio_tab)
        self.from_file_button.setObjectName('from_file_button')
        self.audio_buttons_layout.addWidget(self.from_file_button)
        self.from_media_button = QtWidgets.QPushButton(self.audio_tab)
        self.from_media_button.setObjectName('from_media_button')
        self.audio_buttons_layout.addWidget(self.from_media_button)
        self.audio_remove_button = QtWidgets.QPushButton(self.audio_tab)
        self.audio_remove_button.setObjectName('audio_remove_button')
        self.audio_buttons_layout.addWidget(self.audio_remove_button)
        self.audio_remove_all_button = QtWidgets.QPushButton(self.audio_tab)
        self.audio_remove_all_button.setObjectName('audio_remove_all_button')
        self.audio_buttons_layout.addWidget(self.audio_remove_all_button)
        self.audio_buttons_layout.addStretch(1)
        self.up_button = create_button(self, 'up_button', role='up', click=self.on_up_button_clicked)
        self.down_button = create_button(self, 'down_button', role='down', click=self.on_down_button_clicked)
        self.audio_buttons_layout.addWidget(self.up_button)
        self.audio_buttons_layout.addWidget(self.down_button)
        self.audio_layout.addLayout(self.audio_buttons_layout)
        self.song_tab_widget.addTab(self.audio_tab, '')
        # Last few bits
        self.dialog_layout.addWidget(self.song_tab_widget)
        self.bottom_layout = QtWidgets.QHBoxLayout()
        self.bottom_layout.setObjectName('bottom_layout')
        self.warning_label = QtWidgets.QLabel(edit_song_dialog)
        self.warning_label.setObjectName('warning_label')
        self.bottom_layout.addWidget(self.warning_label)
        self.button_box = create_button_box(edit_song_dialog, 'button_box', ['cancel', 'save', 'help'])
        self.bottom_layout.addWidget(self.button_box)
        self.dialog_layout.addLayout(self.bottom_layout)
        self.retranslate_ui(edit_song_dialog)

    def retranslate_ui(self, edit_song_dialog):
        """
        Translate the UI on the fly.
        """
        edit_song_dialog.setWindowTitle(translate('SongsPlugin.EditSongForm', 'Song Editor'))
        self.title_label.setText(translate('SongsPlugin.EditSongForm', '&Title:'))
        self.alternative_title_label.setText(translate('SongsPlugin.EditSongForm', 'Alt&ernate title:'))
        self.lyrics_label.setText(translate('SongsPlugin.EditSongForm', '&Lyrics:'))
        self.verse_order_label.setText(translate('SongsPlugin.EditSongForm', '&Verse order:'))
        self.verse_add_button.setText(UiStrings().Add)
        self.verse_edit_button.setText(UiStrings().Edit)
        self.verse_edit_all_button.setText(translate('SongsPlugin.EditSongForm', 'Ed&it All'))
        self.verse_delete_button.setText(UiStrings().Delete)
        self.song_tab_widget.setTabText(self.song_tab_widget.indexOf(self.lyrics_tab),
                                        translate('SongsPlugin.EditSongForm', 'Title && Lyrics'))
        self.authors_group_box.setTitle(SongStrings().Authors)
        self.author_add_button.setText(translate('SongsPlugin.EditSongForm', '&Add to Song'))
        self.author_edit_button.setText(translate('SongsPlugin.EditSongForm', '&Edit Author Type'))
        self.author_remove_button.setText(translate('SongsPlugin.EditSongForm', '&Remove'))
        self.maintenance_button.setText(translate('SongsPlugin.EditSongForm', '&Manage Authors, Topics, Songbooks'))
        self.topics_group_box.setTitle(SongStrings().Topics)
        self.topic_add_button.setText(translate('SongsPlugin.EditSongForm', 'A&dd to Song'))
        self.topic_remove_button.setText(translate('SongsPlugin.EditSongForm', 'R&emove'))
        self.songbook_group_box.setTitle(SongStrings().SongBooks)
        self.songbook_add_button.setText(translate('SongsPlugin.EditSongForm', 'Add &to Song'))
        self.songbook_remove_button.setText(translate('SongsPlugin.EditSongForm', 'Re&move'))
        self.song_tab_widget.setTabText(self.song_tab_widget.indexOf(self.authors_tab),
                                        translate('SongsPlugin.EditSongForm', 'Authors, Topics && Songbooks'))
        self.theme_group_box.setTitle(UiStrings().Theme)
        self.theme_add_button.setText(translate('SongsPlugin.EditSongForm', 'New &Theme'))
        self.rights_group_box.setTitle(translate('SongsPlugin.EditSongForm', 'Copyright Information'))
        self.copyright_insert_button.setText(SongStrings().CopyrightSymbol)
        self.ccli_label.setText(UiStrings().CCLISongNumberLabel)
        self.comments_group_box.setTitle(translate('SongsPlugin.EditSongForm', 'Comments'))
        self.song_tab_widget.setTabText(self.song_tab_widget.indexOf(self.theme_tab),
                                        translate('SongsPlugin.EditSongForm', 'Theme, Copyright Info && Comments'))
        self.song_tab_widget.setTabText(self.song_tab_widget.indexOf(self.audio_tab),
                                        translate('SongsPlugin.EditSongForm', 'Linked Audio'))
        self.from_file_button.setText(translate('SongsPlugin.EditSongForm', 'Add &File(s)'))
        self.from_media_button.setText(translate('SongsPlugin.EditSongForm', 'Add &Media'))
        self.audio_remove_button.setText(translate('SongsPlugin.EditSongForm', '&Remove'))
        self.audio_remove_all_button.setText(translate('SongsPlugin.EditSongForm', 'Remove &All'))
        self.not_all_verses_used_warning = \
            translate('SongsPlugin.EditSongForm', '<strong>Warning:</strong> Not all of the verses are in use.')
        self.no_verse_order_entered_warning =  \
            translate('SongsPlugin.EditSongForm', '<strong>Warning:</strong> You have not entered a verse order.')


def create_combo_box(parent, name, editable=True):
    """
    Utility method to generate a standard combo box for this dialog.

    :param parent: The parent widget for this combo box.
    :param name: The object name
    """
    combo_box = QtWidgets.QComboBox(parent)
    combo_box.setSizeAdjustPolicy(QtWidgets.QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
    combo_box.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
    combo_box.setEditable(editable)
    combo_box.setInsertPolicy(QtWidgets.QComboBox.InsertPolicy.NoInsert)
    combo_box.setObjectName(name)
    return combo_box
