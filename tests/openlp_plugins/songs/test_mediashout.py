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
Test the MediaShout importer
"""
from collections import namedtuple
from unittest.mock import MagicMock, call, patch

import pytest

from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings


try:
    from openlp.plugins.songs.lib.importers.mediashout import MediaShoutImport
    CAN_RUN_TESTS = True
except ImportError:
    class MediaShoutImport:
        pass

    CAN_RUN_TESTS = False


pytestmark = pytest.mark.skipif(not CAN_RUN_TESTS, reason='Not Windows, skipping test')


@pytest.fixture
def importer(registry: Registry, settings: Settings):
    return MediaShoutImport(MagicMock(), file_path='mediashout.db')


def test_constructor(importer: MediaShoutImport):
    """
    Test the MediaShoutImport constructor
    """
    # GIVEN: A MediaShoutImport class
    # WHEN: It is created
    # THEN: It should not be None
    assert importer is not None


@patch('openlp.plugins.songs.lib.importers.mediashout.pyodbc')
def test_do_import_fails_to_connect(mocked_pyodbc: MagicMock, importer: MediaShoutImport):
    """
    Test that do_import exits early when unable to connect to the database
    """
    # GIVEN: A MediaShoutImport instance and pyodbc unable to connect
    mocked_pyodbc.connect.side_effect = Exception('Unable to connect')

    # WHEN: do_import is called
    with patch.object(importer, 'log_error') as mocked_log_error:
        importer.do_import()

    # THEN: The songs should have been imported
    mocked_log_error.assert_called_once_with('mediashout.db', 'Unable to open the MediaShout database.')


@patch('openlp.plugins.songs.lib.importers.mediashout.pyodbc')
def test_do_import(mocked_pyodbc: MagicMock, importer: MediaShoutImport):
    """
    Test the MediaShoutImport do_import method
    """
    SongRecord = namedtuple('SongRecord', 'Record, Title, Author, Copyright, SongID, CCLI, Notes')
    VerseRecord = namedtuple('VerseRecord', 'Type, Number, Text')
    PlayOrderRecord = namedtuple('PlayOrderRecord', 'Type, Number, POrder')
    ThemeRecord = namedtuple('ThemeRecord', 'Name')
    GroupRecord = namedtuple('GroupRecord', 'Name')
    song = SongRecord(1, 'Amazing Grace', 'William Wilberforce', 'Public Domain', 1, '654321', '')
    verse = VerseRecord('Verse', 1, 'Amazing grace, how sweet the sound\nThat saved a wretch like me')
    play_order = PlayOrderRecord('Verse', 1, 1)
    theme = ThemeRecord('Grace')
    group = GroupRecord('Hymns')

    # GIVEN: A MediaShoutImport instance and a bunch of stuff mocked out
    mocked_cursor = MagicMock()
    mocked_cursor.fetchall.side_effect = [[song], [verse], [play_order], [theme], [group]]
    mocked_cursor.tables.return_value.fetchone.return_value = True
    mocked_connection = MagicMock()
    mocked_connection.cursor.return_value = mocked_cursor
    mocked_pyodbc.connect.return_value = mocked_connection

    # WHEN: do_import is called
    with patch.object(importer, 'import_wizard'), \
            patch.object(importer, 'process_song') as mocked_process_song:
        importer.do_import()

    # THEN: The songs should have been imported
    expected_execute_calls = [
        call('SELECT Record, Title, Author, Copyright, SongID, CCLI, Notes FROM Songs ORDER BY Title'),
        call('SELECT Type, Number, Text FROM Verses WHERE Record = ? ORDER BY Type, Number', 1.0),
        call('SELECT Type, Number, POrder FROM PlayOrder WHERE Record = ? ORDER BY POrder', 1.0),
        call('SELECT Name FROM Themes INNER JOIN SongThemes ON SongThemes.ThemeId = Themes.ThemeId '
             'WHERE SongThemes.Record = ?', 1.0),
        call('SELECT Name FROM Groups INNER JOIN SongGroups ON SongGroups.GroupId = Groups.GroupId '
             'WHERE SongGroups.Record = ?', 1.0)
    ]
    assert expected_execute_calls == mocked_cursor.execute.call_args_list
    mocked_process_song.assert_called_once_with(song, [verse], [play_order], [theme, group])


@patch('openlp.plugins.songs.lib.importers.mediashout.pyodbc')
def test_do_import_without_topics(mocked_pyodbc: MagicMock, importer: MediaShoutImport):
    """
    Test the MediaShoutImport do_import method with the Themes and Groups tables don't exist
    """
    SongRecord = namedtuple('SongRecord', 'Record, Title, Author, Copyright, SongID, CCLI, Notes')
    VerseRecord = namedtuple('VerseRecord', 'Type, Number, Text')
    PlayOrderRecord = namedtuple('PlayOrderRecord', 'Type, Number, POrder')
    song = SongRecord(1, 'Amazing Grace', 'William Wilberforce', 'Public Domain', 1, '654321', '')
    verse = VerseRecord('Verse', 1, 'Amazing grace, how sweet the sound\nThat saved a wretch like me')
    play_order = PlayOrderRecord('Verse', 1, 1)

    # GIVEN: A MediaShoutImport instance and a bunch of stuff mocked out
    mocked_cursor = MagicMock()
    mocked_cursor.fetchall.side_effect = [[song], [verse], [play_order]]
    mocked_cursor.tables.return_value.fetchone.return_value = False
    mocked_connection = MagicMock()
    mocked_connection.cursor.return_value = mocked_cursor
    mocked_pyodbc.connect.return_value = mocked_connection

    # WHEN: do_import is called
    with patch.object(importer, 'import_wizard'), \
            patch.object(importer, 'process_song') as mocked_process_song:
        importer.do_import()

    # THEN: The songs should have been imported
    expected_execute_calls = [
        call('SELECT Record, Title, Author, Copyright, SongID, CCLI, Notes FROM Songs ORDER BY Title'),
        call('SELECT Type, Number, Text FROM Verses WHERE Record = ? ORDER BY Type, Number', 1.0),
        call('SELECT Type, Number, POrder FROM PlayOrder WHERE Record = ? ORDER BY POrder', 1.0)
    ]
    assert expected_execute_calls == mocked_cursor.execute.call_args_list
    mocked_process_song.assert_called_once_with(song, [verse], [play_order], [])


@patch('openlp.plugins.songs.lib.importers.mediashout.pyodbc')
def test_do_import_breaks_on_stop(mocked_pyodbc: MagicMock, importer: MediaShoutImport):
    """
    Test the MediaShoutImport do_import stops when the user presses the cancel button
    """
    SongRecord = namedtuple('SongRecord', 'Record, Title, Author, Copyright, SongID, CCLI, Notes')
    song = SongRecord(1, 'Amazing Grace', 'William Wilberforce', 'Public Domain', 1, '654321', '')

    # GIVEN: A MediaShoutImport instance and a bunch of stuff mocked out
    mocked_cursor = MagicMock()
    mocked_cursor.fetchall.return_value = [song]
    mocked_connection = MagicMock()
    mocked_connection.cursor.return_value = mocked_cursor
    mocked_pyodbc.connect.return_value = mocked_connection

    # WHEN: do_import is called, but cancelled
    with patch.object(importer, 'import_wizard'), \
            patch.object(importer, 'process_song') as mocked_process_song:
        importer.stop_import_flag = True
        importer.do_import()

    # THEN: The songs should have been imported
    mocked_cursor.execute.assert_called_once_with(
        'SELECT Record, Title, Author, Copyright, SongID, CCLI, Notes FROM Songs ORDER BY Title')
    mocked_process_song.assert_not_called()


def test_process_song(importer: MediaShoutImport):
    """
    Test the process_song method of the MediaShoutImport
    """
    # GIVEN: An importer and a song
    SongRecord = namedtuple('SongRecord', 'Record, Title, Author, Copyright, SongID, CCLI, Notes')
    VerseRecord = namedtuple('VerseRecord', 'Type, Number, Text')
    PlayOrderRecord = namedtuple('PlayOrderRecord', 'Type, Number, POrder')
    ThemeRecord = namedtuple('ThemeRecord', 'Name')
    GroupRecord = namedtuple('GroupRecord', 'Name')
    song = SongRecord(1, 'Amazing Grace', 'William Wilberforce', 'Public Domain', 'Hymns', '654321',
                      'Great old hymn')
    verse = VerseRecord(0, 1, 'Amazing grace, how sweet the sound\nThat saved a wretch like me')
    play_order = PlayOrderRecord(0, 1, 1)
    theme = ThemeRecord('Grace')
    group = GroupRecord('Hymns')

    # WHEN: A song is processed
    with patch.object(importer, 'set_defaults') as mocked_set_defaults, \
            patch.object(importer, 'parse_author') as mocked_parse_author, \
            patch.object(importer, 'add_copyright') as mocked_add_copyright, \
            patch.object(importer, 'add_verse') as mocked_add_verse, \
            patch.object(importer, 'finish') as mocked_finish:
        importer.topics = []
        importer.verse_order_list = []
        importer.process_song(song, [verse], [play_order], [theme, group])

    # THEN: It should be added to the database
    mocked_set_defaults.assert_called_once_with()
    assert 'Amazing Grace' == importer.title
    mocked_parse_author.assert_called_once_with('William Wilberforce')
    mocked_add_copyright.assert_called_once_with('Public Domain')
    assert 'Great old hymn' == importer.comments
    assert ['Grace', 'Hymns'] == importer.topics
    assert 'Hymns' == importer.song_book_name
    assert '' == importer.song_number
    mocked_add_verse.assert_called_once_with(
        'Amazing grace, how sweet the sound\nThat saved a wretch like me', 'V1')
    assert ['V1'] == importer.verse_order_list
    mocked_finish.assert_called_once_with()


def test_process_song_with_song_number(importer: MediaShoutImport):
    """
    Test the process_song method with a song that has a song number
    """
    # GIVEN: An importer and a song
    SongRecord = namedtuple('SongRecord', 'Record, Title, Author, Copyright, SongID, CCLI, Notes')
    VerseRecord = namedtuple('VerseRecord', 'Type, Number, Text')
    PlayOrderRecord = namedtuple('PlayOrderRecord', 'Type, Number, POrder')
    ThemeRecord = namedtuple('ThemeRecord', 'Name')
    GroupRecord = namedtuple('GroupRecord', 'Name')
    song = SongRecord(1, 'Amazing Grace', 'William Wilberforce', 'Public Domain', 'Hymns-2', '654321',
                      'Great old hymn')
    verse = VerseRecord(0, 1, 'Amazing grace, how sweet the sound\nThat saved a wretch like me')
    play_order = PlayOrderRecord(0, 1, 1)
    theme = ThemeRecord('Grace')
    group = GroupRecord('Hymns')

    # WHEN: A song is processed
    with patch.object(importer, 'set_defaults') as mocked_set_defaults, \
            patch.object(importer, 'parse_author') as mocked_parse_author, \
            patch.object(importer, 'add_copyright') as mocked_add_copyright, \
            patch.object(importer, 'add_verse') as mocked_add_verse, \
            patch.object(importer, 'finish') as mocked_finish:
        importer.topics = []
        importer.verse_order_list = []
        importer.process_song(song, [verse], [play_order], [theme, group])

    # THEN: It should be added to the database
    mocked_set_defaults.assert_called_once_with()
    assert 'Amazing Grace' == importer.title
    mocked_parse_author.assert_called_once_with('William Wilberforce')
    mocked_add_copyright.assert_called_once_with('Public Domain')
    assert 'Great old hymn' == importer.comments
    assert ['Grace', 'Hymns'] == importer.topics
    assert 'Hymns' == importer.song_book_name
    assert '2' == importer.song_number
    mocked_add_verse.assert_called_once_with(
        'Amazing grace, how sweet the sound\nThat saved a wretch like me', 'V1')
    assert ['V1'], importer.verse_order_list
    mocked_finish.assert_called_once_with()
