# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2019 OpenLP Developers                                   #
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
The :mod:`~openlp.core.ui.media.playertab` module holds the configuration tab for the media stuff.
"""

from PyQt5 import QtWidgets

from openlp.core.common import is_linux, is_win
from openlp.core.common.i18n import translate
from openlp.core.common.settings import Settings
from openlp.core.lib.settingstab import SettingsTab
from openlp.core.ui.icons import UiIcons

LINUX_STREAM = 'v4l2:///dev/video0'
WIN_STREAM = 'dshow:// :dshow-vdev='

#from PyQt5.QtMultimedia import QCameraInfo, QAudioDeviceInfo, QAudio

#print('Video input:')
#for cam in QCameraInfo.availableCameras():
#    print('===============')
 ###   print(cam.deviceName())
  #  print(cam.description())#
#print()
#print('Audio input:')
#for au in QAudioDeviceInfo.availableDevices(QAudio.AudioInput):
#    print('===============')
#    print(au.deviceName())


class MediaTab(SettingsTab):
    """
    MediaTab is the Media settings tab in the settings dialog.
    """
    def __init__(self, parent):
        """
        Constructor
        """
        # self.media_players = Registry().get('media_controller').media_players
        # self.saved_used_players = None
        self.icon_path = UiIcons().video
        player_translated = translate('OpenLP.MediaTab', 'Media')
        super(MediaTab, self).__init__(parent, 'Media', player_translated)

    def setup_ui(self):
        """
        Set up the UI
        """
        self.setObjectName('MediaTab')
        super(MediaTab, self).setup_ui()
        self.live_media_group_box = QtWidgets.QGroupBox(self.left_column)
        self.live_media_group_box.setObjectName('live_media_group_box')
        self.media_layout = QtWidgets.QVBoxLayout(self.live_media_group_box)
        self.media_layout.setObjectName('live_media_layout')
        self.auto_start_check_box = QtWidgets.QCheckBox(self.live_media_group_box)
        self.auto_start_check_box.setObjectName('auto_start_check_box')
        self.media_layout.addWidget(self.auto_start_check_box)
        self.left_layout.addWidget(self.live_media_group_box)
        self.stream_media_group_box = QtWidgets.QGroupBox(self.left_column)
        self.stream_media_group_box.setObjectName('stream_media_group_box')
        self.stream_media_layout = QtWidgets.QHBoxLayout(self.stream_media_group_box)
        self.stream_media_layout.setObjectName('live_media_layout')
        self.stream_media_layout.setContentsMargins(0, 0, 0, 0)
        self.stream_edit = QtWidgets.QPlainTextEdit(self)
        self.stream_media_layout.addWidget(self.stream_edit)
        self.browse_button = QtWidgets.QToolButton(self)
        self.browse_button.setIcon(UiIcons().undo)
        self.stream_media_layout.addWidget(self.browse_button)
        self.left_layout.addWidget(self.stream_media_group_box)
        self.left_layout.addWidget(self.stream_media_group_box)
        self.left_layout.addStretch()
        self.right_layout.addStretch()
        # # Signals and slots
        self.browse_button.clicked.connect(self.on_revert)

    def retranslateUi(self):
        """
        Translate the UI on the fly
        """
        self.live_media_group_box.setTitle(translate('MediaPlugin.MediaTab', 'Live Media'))
        self.stream_media_group_box.setTitle(translate('MediaPlugin.MediaTab', 'Stream Media Command'))
        self.auto_start_check_box.setText(translate('MediaPlugin.MediaTab', 'Start automatically'))

    def load(self):
        """
        Load the settings
        """
        self.auto_start_check_box.setChecked(Settings().value(self.settings_section + '/media auto start'))
        self.stream_edit.setPlainText(Settings().value(self.settings_section + '/stream command'))
        if not self.stream_edit.toPlainText():
            if is_linux:
                self.stream_edit.setPlainText(LINUX_STREAM)
            elif is_win:
                self.stream_edit.setPlainText(WIN_STREAM)

    def save(self):
        """
        Save the settings
        """
        setting_key = self.settings_section + '/media auto start'
        if Settings().value(setting_key) != self.auto_start_check_box.checkState():
            Settings().setValue(setting_key, self.auto_start_check_box.checkState())
        # settings = Settings()
        # settings.beginGroup(self.settings_section)
        # settings.setValue('background color', self.background_color)
        # settings.endGroup()
        # old_players, override_player = get_media_players()
        # if self.used_players != old_players:
        #     # clean old Media stuff
        #     set_media_players(self.used_players, override_player)
        #     self.settings_form.register_post_process('mediaitem_suffix_reset')
        #     self.settings_form.register_post_process('mediaitem_media_rebuild')
        #     self.settings_form.register_post_process('config_screen_changed')

    def post_set_up(self, post_update=False):
        """
        Late setup for players as the MediaController has to be initialised first.

        :param post_update: Indicates if called before or after updates.
        """
        pass
        # for key, player in self.media_players.items():
        #     player = self.media_players[key]
        #     checkbox = MediaQCheckBox(self.media_player_group_box)
        #     checkbox.setEnabled(player.available)
        #     checkbox.setObjectName(player.name + '_check_box')
        #     checkbox.setToolTip(player.get_info())
        #     checkbox.set_player_name(player.name)
        #     self.player_check_boxes[player.name] = checkbox
        #     checkbox.stateChanged.connect(self.on_player_check_box_changed)
        #     self.media_player_layout.addWidget(checkbox)
        #     if player.available and player.name in self.used_players:
        #         checkbox.setChecked(True)
        #     else:
        #         checkbox.setChecked(False)
        # self.update_player_list()
        # self.retranslate_players()

    def on_revert(self):
        pass
