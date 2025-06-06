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
This module contains tests for the WorshipCenter Pro song importer.
"""
from unittest.mock import MagicMock, patch

import pytest

from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings

try:
    import pyodbc
    from openlp.plugins.songs.lib.importers.worshipcenterpro import WorshipCenterProImport
    CAN_RUN_TESTS = True
except ImportError:
    class WorshipCenterProImport:
        pass

    pyodbc = MagicMock()
    CAN_RUN_TESTS = False


pytestmark = pytest.mark.skipif(not CAN_RUN_TESTS, reason='Cannot run WorshipCenterPro tests')


class DBTestRecord(object):
    """
    Microsoft Access Driver is not available on non Microsoft Systems for this reason the :class:`FakeRecord` is used
    to simulate a recordset that would be returned by pyobdc.
    """
    def __init__(self, id_, field, value):
        # The case of the following instance variables is important as it needs to be the same as the ones in use in the
        # WorshipCenter Pro database.
        self.ID = id_
        self.Field = field
        self.Value = value


class WorshipCenterProImportLogger(WorshipCenterProImport):
    """
    This class logs changes in the title instance variable
    """
    _title_assignment_list = None

    def __init__(self, manager):
        WorshipCenterProImport.__init__(self, manager, file_paths=[])
        self._title_assignment_list = []

    @property
    def title(self):
        return self._title_assignment_list[-1]

    @title.setter
    def title(self, title):
        try:
            self._title_assignment_list.append(title)
        except AttributeError:
            self._title_assignment_list = [title]


RECORDSET_TEST_DATA = [DBTestRecord(1, 'TITLE', 'Amazing Grace'),
                       DBTestRecord(1, 'AUTHOR', 'John Newton'),
                       DBTestRecord(1, 'CCLISONGID', '12345'),
                       DBTestRecord(1, 'COMMENTS', 'The original version'),
                       DBTestRecord(1, 'COPY', 'Public Domain'),
                       DBTestRecord(1, 'SUBJECT', 'Grace'),
                       DBTestRecord(
                           1, 'LYRICS',
                           '<INTRO>Amazing grace! How&crlf;sweet the sound&crlf;That saved a wretch like me!&crlf;'
                           'I once was lost,&crlf;but now am found;&crlf;Was blind, but now I see.&crlf;&crlf;'
                           '<PRECHORUS>\'Twas grace that&crlf;taught my heart to fear,&crlf;'
                           'And grace my fears relieved;&crlf;'
                           'How precious did&crlf;that grace appear&crlf;The hour I first believed.&crlf;&crlf;'
                           '<CHORUS>Through many dangers,&crlf;toils and snares,&crlf;I have already come;&crlf;'
                           '\'Tis grace hath brought&crlf;me safe thus far,&crlf;'
                           'And grace will lead me home.&crlf;&crlf;'
                           '<REFRAIN>The Lord has&crlf;promised good to me,&crlf;'
                           'His Word my hope secures;&crlf;He will my Shield&crlf;and Portion be,&crlf;'
                           'As long as life endures.&crlf;&crlf;'
                           '<BRIDGE>Yea, when this flesh&crlf;and heart shall fail,&crlf;'
                           'And mortal life shall cease,&crlf;I shall possess,&crlf;within the veil,&crlf;'
                           'A life of joy and peace.&crlf;&crlf;'
                           '<TAG>The earth shall soon&crlf;dissolve like snow,&crlf;'
                           'The sun forbear to shine;&crlf;But God, Who called&crlf;me here below,&crlf;'
                           'Shall be forever mine.&crlf;&crlf;'
                           '<END>When we\'ve been there&crlf;ten thousand years,&crlf;'
                           'Bright shining as the sun,&crlf;We\'ve no less days to&crlf;sing God\'s praise&crlf;'
                           'Than when we\'d first begun.&crlf;&crlf;'),
                       DBTestRecord(2, 'TITLE', 'Beautiful Garden Of Prayer, The'),
                       DBTestRecord(
                           2, 'LYRICS',
                           'There\'s a garden where&crlf;Jesus is waiting,&crlf;'
                           'There\'s a place that&crlf;is wondrously fair,&crlf;For it glows with the&crlf;'
                           'light of His presence.&crlf;\'Tis the beautiful&crlf;garden of prayer.&crlf;&crlf;'
                           'Oh, the beautiful garden,&crlf;the garden of prayer!&crlf;Oh, the beautiful&crlf;'
                           'garden of prayer!&crlf;There my Savior awaits,&crlf;and He opens the gates&crlf;'
                           'To the beautiful&crlf;garden of prayer.&crlf;&crlf;There\'s a garden where&crlf;'
                           'Jesus is waiting,&crlf;And I go with my&crlf;burden and care,&crlf;'
                           'Just to learn from His&crlf;lips words of comfort&crlf;In the beautiful&crlf;'
                           'garden of prayer.&crlf;&crlf;There\'s a garden where&crlf;Jesus is waiting,&crlf;'
                           'And He bids you to come,&crlf;meet Him there;&crlf;Just to bow and&crlf;'
                           'receive a new blessing&crlf;In the beautiful&crlf;garden of prayer.&crlf;&crlf;')]
SONG_TEST_DATA = [{'title': 'Amazing Grace',
                   'verses': [
                       ('Amazing grace! How\nsweet the sound\nThat saved a wretch like me!\nI once was lost,\n'
                        'but now am found;\nWas blind, but now I see.', 'i'),
                       ('\'Twas grace that\ntaught my heart to fear,\nAnd grace my fears relieved;\nHow precious did\n'
                        'that grace appear\nThe hour I first believed.', 'p'),
                       ('Through many dangers,\ntoils and snares,\nI have already come;\n\'Tis grace hath brought\n'
                        'me safe thus far,\nAnd grace will lead me home.', 'c'),
                       ('The Lord has\npromised good to me,\nHis Word my hope secures;\n'
                        'He will my Shield\nand Portion be,\nAs long as life endures.', 'c'),
                       ('Yea, when this flesh\nand heart shall fail,\nAnd mortal life shall cease,\nI shall possess,\n'
                        'within the veil,\nA life of joy and peace.', 'b'),
                       ('The earth shall soon\ndissolve like snow,\nThe sun forbear to shine;\nBut God, Who called\n'
                        'me here below,\nShall be forever mine.', 'o'),
                       ('When we\'ve been there\nten thousand years,\nBright shining as the sun,\n'
                        'We\'ve no less days to\nsing God\'s praise\nThan when we\'d first begun.', 'e')],
                   'author': 'John Newton',
                   'comments': 'The original version',
                   'copyright': 'Public Domain'},
                  {'title': 'Beautiful Garden Of Prayer, The',
                   'verses': [
                       ('There\'s a garden where\nJesus is waiting,\nThere\'s a place that\nis wondrously fair,\n'
                        'For it glows with the\nlight of His presence.\n\'Tis the beautiful\ngarden of prayer.', 'v'),
                       ('Oh, the beautiful garden,\nthe garden of prayer!\nOh, the beautiful\ngarden of prayer!\n'
                        'There my Savior awaits,\nand He opens the gates\nTo the beautiful\ngarden of prayer.', 'v'),
                       ('There\'s a garden where\nJesus is waiting,\nAnd I go with my\nburden and care,\n'
                        'Just to learn from His\nlips words of comfort\nIn the beautiful\ngarden of prayer.', 'v'),
                       ('There\'s a garden where\nJesus is waiting,\nAnd He bids you to come,\nmeet Him there;\n'
                        'Just to bow and\nreceive a new blessing\nIn the beautiful\ngarden of prayer.', 'v')]}]


@pytest.fixture
def importer(registry: Registry, settings: Settings):
    with patch('openlp.plugins.songs.lib.importers.worshipcenterpro.SongImport'):
        yield WorshipCenterProImportLogger(MagicMock())


def test_create_importer(importer: WorshipCenterProImportLogger):
    """
    Test creating an instance of the WorshipCenter Pro file importer
    """
    # GIVEN: A mocked out SongImport class, and a mocked out "manager"
    # WHEN: An importer object is created
    # THEN: The importer object should not be None
    assert importer is not None, 'Import should not be none'


@patch('openlp.plugins.songs.lib.importers.worshipcenterpro.translate')
@patch('openlp.plugins.songs.lib.importers.worshipcenterpro.pyodbc.connect')
@pytest.mark.parametrize('error', [pyodbc.DatabaseError, pyodbc.IntegrityError, pyodbc.InternalError,
                                   pyodbc.OperationalError])
def test_pyodbc_exception(mocked_pyodbc_connect: MagicMock, mocked_translate: MagicMock,
                          importer: WorshipCenterProImportLogger, error: Exception):
    """
    Test that exceptions raised by pyodbc are handled
    """
    # GIVEN: A mocked out SongImport class, a mocked out pyodbc module, a mocked out translate method,
    #       a mocked "manager" and a mocked out log_error method.
    mocked_log_error = MagicMock()
    mocked_translate.return_value = 'Translated Text'
    importer.log_error = mocked_log_error
    importer.import_source = 'import_source'
    mocked_pyodbc_connect.side_effect = error

    # WHEN: Calling the do_import method
    return_value = importer.do_import()

    # THEN: do_import should return None, and pyodbc, translate & log_error are called with known calls
    assert return_value is None, 'do_import should return None when pyodbc raises an exception.'
    mocked_pyodbc_connect.assert_called_with('DRIVER={Microsoft Access Driver (*.mdb)};DBQ=import_source')
    mocked_translate.assert_called_with('SongsPlugin.WorshipCenterProImport',
                                        'Unable to connect the WorshipCenter Pro database.')
    mocked_log_error.assert_called_with('import_source', 'Translated Text')


@patch('openlp.plugins.songs.lib.importers.worshipcenterpro.translate')
@patch('openlp.plugins.songs.lib.importers.worshipcenterpro.pyodbc')
def test_song_import(mocked_pyodbc: MagicMock, mocked_translate: MagicMock,
                     importer: WorshipCenterProImportLogger):
    """
    Test that a simulated WorshipCenter Pro recordset is imported correctly
    """
    # GIVEN: A mocked out SongImport class, a mocked out pyodbc module with a simulated recordset, a mocked out
    #       translate method,  a mocked "manager", add_verse method & mocked_finish method.
    mocked_import_wizard = MagicMock()
    mocked_add_verse = MagicMock()
    mocked_parse_author = MagicMock()
    mocked_add_comment = MagicMock()
    mocked_add_copyright = MagicMock()
    mocked_finish = MagicMock()
    mocked_pyodbc.connect.return_value.cursor.return_value.fetchall.return_value = RECORDSET_TEST_DATA
    mocked_translate.return_value = 'Translated Text'
    importer.import_source = 'import_source'
    importer.import_wizard = mocked_import_wizard
    importer.add_verse = mocked_add_verse
    importer.parse_author = mocked_parse_author
    importer.add_comment = mocked_add_comment
    importer.add_copyright = mocked_add_copyright
    importer.stop_import_flag = False
    importer.finish = mocked_finish

    # WHEN: Calling the do_import method
    return_value = importer.do_import()

    # THEN: do_import should return None, and pyodbc, import_wizard, importer.title and add_verse are called
    # with known calls
    assert return_value is None, 'do_import should return None when pyodbc raises an exception.'
    mocked_pyodbc.connect.assert_called_with('DRIVER={Microsoft Access Driver (*.mdb)};DBQ=import_source')
    mocked_pyodbc.connect.return_value.cursor.assert_any_call()
    mocked_pyodbc.connect.return_value.cursor.return_value.execute.assert_called_with(
        'SELECT ID, Field, Value FROM __SONGDATA')
    mocked_pyodbc.connect.return_value.cursor.return_value.fetchall.assert_any_call()
    mocked_import_wizard.progress_bar.setMaximum.assert_called_with(2)
    add_verse_call_count = 0
    for song_data in SONG_TEST_DATA:
        title_value = song_data['title']
        assert title_value in importer._title_assignment_list, 'title should have been set to %s' % title_value
        verse_calls = song_data['verses']
        add_verse_call_count += len(verse_calls)
        for call in verse_calls:
            mocked_add_verse.assert_any_call(*call)
        if 'author' in song_data:
            mocked_parse_author.assert_any_call(song_data['author'])
        if 'comments' in song_data:
            mocked_add_comment.assert_any_call(song_data['comments'])
        if 'copyright' in song_data:
            mocked_add_copyright.assert_any_call(song_data['copyright'])
        if 'subject' in song_data:
            mocked_add_copyright.assert_any_call(song_data['subject'])
    assert mocked_add_verse.call_count == add_verse_call_count, 'Incorrect number of calls made to add_verse'


@patch('openlp.plugins.songs.lib.importers.worshipcenterpro.translate')
@patch('openlp.plugins.songs.lib.importers.worshipcenterpro.pyodbc')
def test_song_import_stop(mocked_pyodbc: MagicMock, mocked_translate: MagicMock,
                          importer: WorshipCenterProImportLogger):
    """Test that the song importer stops when the flag is set"""
    mocked_import_wizard = MagicMock()
    mocked_add_verse = MagicMock()
    mocked_parse_author = MagicMock()
    mocked_add_comment = MagicMock()
    mocked_add_copyright = MagicMock()
    mocked_finish = MagicMock()
    mocked_pyodbc.connect().cursor().fetchall.return_value = RECORDSET_TEST_DATA
    mocked_translate.return_value = 'Translated Text'
    importer.import_source = 'import_source'
    importer.import_wizard = mocked_import_wizard
    importer.add_verse = mocked_add_verse
    importer.parse_author = mocked_parse_author
    importer.add_comment = mocked_add_comment
    importer.add_copyright = mocked_add_copyright
    importer.stop_import_flag = True
    importer.finish = mocked_finish

    # WHEN: Calling the do_import method
    importer.do_import()

    # THEN: No songs should have been imported
    assert len(importer._title_assignment_list) == 0
    mocked_finish.assert_not_called()
