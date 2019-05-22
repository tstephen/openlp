# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

##########################################################################
# OpenLP - Open Source Lyrics Projection                                 #
# ---------------------------------------------------------------------- #
# Copyright (c) 2008-2019 OpenLP Developers                              #
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
This module contains tests for the Words of Worship song importer.
"""
from tests.helpers.songfileimport import SongImportTestHelper
from tests.utils.constants import RESOURCE_PATH


TEST_PATH = RESOURCE_PATH / 'songs' / 'wordsofworship'


class TestWordsOfWorshipFileImport(SongImportTestHelper):

    def __init__(self, *args, **kwargs):
        self.importer_class_name = 'WordsOfWorshipImport'
        self.importer_module_name = 'wordsofworship'
        super(TestWordsOfWorshipFileImport, self).__init__(*args, **kwargs)

    def test_song_import(self):
        """
        Test that loading a Words of Worship file works correctly
        """
        self.file_import([TEST_PATH / 'Amazing Grace (6 Verses).wow-song'],
                         self.load_external_result_data(TEST_PATH / 'Amazing Grace (6 Verses).json'))
        self.file_import([TEST_PATH / 'When morning gilds the skies.wsg'],
                         self.load_external_result_data(TEST_PATH / 'When morning gilds the skies.json'))
        self.file_import([TEST_PATH / 'Holy Holy Holy Lord God Almighty.wow-song'],
                         self.load_external_result_data(TEST_PATH / 'Holy Holy Holy Lord God Almighty.json'))
