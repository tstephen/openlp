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
The :mod:`opspro` module provides the functionality for importing
a OPS Pro database into the OpenLP database.
"""

# WARNING: See https://docs.python.org/2/library/sqlite3.html for value substitution
#          in SQL statements

import logging
import re
import struct

import pyodbc

from openlp.core.common.i18n import translate
from openlp.plugins.songs.lib.importers.songimport import SongImport


log = logging.getLogger(__name__)


class OPSProImport(SongImport):
    """
    The :class:`OPSProImport` class provides the ability to import the
    WorshipCenter Pro Access Database
    """
    def __init__(self, manager, **kwargs):
        """
        Initialise the WorshipCenter Pro importer.
        """
        super(OPSProImport, self).__init__(manager, **kwargs)

    def do_import(self):
        """
        Receive a single file to import.
        """
        password = self.extract_mdb_password()
        try:
            conn = pyodbc.connect('DRIVER={{Microsoft Access Driver (*.mdb)}};DBQ={source};'
                                  'PWD={password}'.format(source=self.import_source, password=password))
        except Exception as e:
            log.warning('Unable to connect the OPS Pro database {source}. {error}'.format(source=self.import_source,
                                                                                          error=str(e)))
            # Unfortunately no specific exception type
            self.log_error(self.import_source, translate('SongsPlugin.OPSProImport',
                                                         'Unable to connect the OPS Pro database.'))
            return
        cursor = conn.cursor()
        cursor.execute('SELECT Song.ID, SongNumber, SongBookName, Title, CopyrightText, Version, Origin FROM Song '
                       'LEFT JOIN SongBook ON Song.SongBookID = SongBook.ID ORDER BY Title')
        songs = cursor.fetchall()
        self.import_wizard.progress_bar.setMaximum(len(songs))
        for song in songs:
            if self.stop_import_flag:
                break
            # Type means: 0=Original, 1=Projection, 2=Own
            cursor.execute('SELECT Lyrics, Type, IsDualLanguage FROM Lyrics WHERE SongID = ? AND Type < 2 '
                           'ORDER BY Type DESC', float(song.ID))
            lyrics = cursor.fetchone()
            cursor.execute('SELECT CategoryName FROM Category INNER JOIN SongCategory '
                           'ON Category.ID = SongCategory.CategoryID WHERE SongCategory.SongID = ? '
                           'ORDER BY CategoryName', float(song.ID))
            topics = cursor.fetchall()
            try:
                self.process_song(song, lyrics, topics)
            except Exception as e:
                self.log_error(self.import_source,
                               translate('SongsPlugin.OPSProImport',
                                         '"{title}" could not be imported. {error}').format(title=song.Title, error=e))

    def process_song(self, song, lyrics, topics):
        """
        Create the song, i.e. title, verse etc.

        The OPS Pro format is a fairly simple text format using tags and anchors/labels. Linebreaks are \r\n.
        Double linebreaks are slide dividers. OPS Pro support dual language using tags.
        Tags are in [], see the liste below:
        [join] are used to separate verses that should be keept on the same slide.
        [split] or [splits] can be used to split a verse over several slides, while still being the same verse
        Dual language tags:
        [trans off] or [vertaal uit] turns dual language mode off for the following text
        [trans on] or [vertaal aan] turns dual language mode on for the following text
        [taal a] means the following lines are language a
        [taal b] means the following lines are language b
        """
        self.set_defaults()
        self.title = song.Title
        if song.CopyrightText:
            for line in song.CopyrightText.splitlines():
                if line.startswith('©') or line.lower().startswith('copyright'):
                    self.add_copyright(line)
                else:
                    self.parse_author(line)
        if song.Origin:
            self.comments = song.Origin
        if song.SongBookName:
            self.song_book_name = song.SongBookName
        if song.SongNumber:
            self.song_number = song.SongNumber
        for topic in topics:
            self.topics.append(topic.CategoryName)
        # Try to split lyrics based on various rules
        if lyrics:
            lyrics_text = lyrics.Lyrics
            verses = re.split(r'\r\n\s*?\r\n', lyrics_text)
            verse_tag_defs = {}
            verse_tag_texts = {}
            for verse_text in verses:
                if verse_text.strip() == '':
                    continue
                verse_def = 'v'
                # Detect verse number
                verse_number = re.match(r'^(\d+)\r\n', verse_text)
                if verse_number:
                    verse_text = re.sub(r'^\d+\r\n', '', verse_text)
                    verse_def = 'v' + verse_number.group(1)
                # Detect verse tags
                elif re.match(r'^.+?:\r\n', verse_text):
                    tag_match = re.match(r'^(.+?):\r\n(.*)', verse_text, flags=re.DOTALL)
                    tag = tag_match.group(1).lower()
                    tag = tag.split(' ')[0]
                    verse_text = tag_match.group(2)
                    if 'refrein' in tag or 'chorus' in tag:
                        verse_def = 'c'
                    elif 'bridge' in tag:
                        verse_def = 'b'
                    verse_tag_defs[tag] = verse_def
                    verse_tag_texts[tag] = verse_text
                # Detect tag reference
                elif re.match(r'^\(.*?\)$', verse_text):
                    tag_match = re.match(r'^\((.*?)\)$', verse_text)
                    tag = tag_match.group(1).lower()
                    if tag in verse_tag_defs:
                        verse_text = verse_tag_texts[tag]
                        verse_def = verse_tag_defs[tag]
                # Detect end tag
                elif re.match(r'^\[slot\]\r\n', verse_text, re.IGNORECASE):
                    verse_def = 'e'
                    verse_text = re.sub(r'^\[slot\]\r\n', '', verse_text, flags=re.IGNORECASE)
                # Replace the join tag with line breaks
                verse_text = verse_text.replace('[join]', '')
                # Replace the split tag with line breaks and an optional split
                verse_text = re.sub(r'\[splits?\]', '\r\n[---]', verse_text)
                # Handle translations
                if lyrics.IsDualLanguage:
                    verse_text = self.handle_translation(verse_text)
                # Remove comments
                verse_text = re.sub(r'\(.*?\)\r\n', '', verse_text, flags=re.IGNORECASE)
                self.add_verse(verse_text, verse_def)
        self.finish()

    def handle_translation(self, verse_text):
        """
        Replace OPS Pro translation tags with a {translation} tag

        :param verse_text: the verse text
        :return: the verse text with replaced tags
        """
        language = None
        translation = True
        translation_verse_text = ''
        start_tag = '{translation}'
        end_tag = '{/translation}'
        verse_text_lines = verse_text.splitlines()
        idx = 0
        while idx < len(verse_text_lines):
            # Detect if translation is turned on or off
            if verse_text_lines[idx] in ['[trans off]', '[vertaal uit]']:
                translation = False
                idx += 1
            elif verse_text_lines[idx] in ['[trans on]', '[vertaal aan]']:
                translation = True
                idx += 1
            elif verse_text_lines[idx] == '[taal a]':
                language = 'a'
                idx += 1
            elif verse_text_lines[idx] == '[taal b]':
                language = 'b'
                idx += 1
            if not idx < len(verse_text_lines):
                break
            # Handle the text based on whether translation is off or on
            if language:
                if language == 'b':
                    translation_verse_text += start_tag
                while idx < len(verse_text_lines) and not verse_text_lines[idx].startswith('['):
                    translation_verse_text += verse_text_lines[idx] + '\r\n'
                    idx += 1
                if language == 'b':
                    translation_verse_text += end_tag
                language = None
            elif translation:
                translation_verse_text += verse_text_lines[idx] + '\r\n'
                idx += 1
                if idx < len(verse_text_lines) and not verse_text_lines[idx].startswith('['):
                    translation_verse_text += start_tag + verse_text_lines[idx] + end_tag + '\r\n'
                    idx += 1
            else:
                translation_verse_text += verse_text_lines[idx] + '\r\n'
                idx += 1
                while idx < len(verse_text_lines) and not verse_text_lines[idx].startswith('['):
                    translation_verse_text += verse_text_lines[idx] + '\r\n'
                    idx += 1
        return translation_verse_text

    def extract_mdb_password(self):
        """
        Extract password from mdb. Based on code from
        http://tutorialsto.com/database/access/crack-access-*.-mdb-all-current-versions-of-the-password.html
        """
        # The definition of 13 bytes as the source XOR Access2000. Encrypted with the corresponding signs are 0x13
        xor_pattern_2k = (0xa1, 0xec, 0x7a, 0x9c, 0xe1, 0x28, 0x34, 0x8a, 0x73, 0x7b, 0xd2, 0xdf, 0x50)
        # Access97 XOR of the source
        xor_pattern_97 = (0x86, 0xfb, 0xec, 0x37, 0x5d, 0x44, 0x9c, 0xfa, 0xc6, 0x5e, 0x28, 0xe6, 0x13)
        with self.import_source.open('rb') as mdb_file:
            mdb_file.seek(0x14)
            version = struct.unpack('B', mdb_file.read(1))[0]
            # Get encrypted logo
            mdb_file.seek(0x62)
            EncrypFlag = struct.unpack('B', mdb_file.read(1))[0]
            # Get encrypted password
            mdb_file.seek(0x42)
            encrypted_password = mdb_file.read(26)
        # "Decrypt" the password based on the version
        decrypted_password = ''
        if version < 0x01:
            # Access 97
            if int(encrypted_password[0] ^ xor_pattern_97[0]) == 0:
                # No password
                decrypted_password = ''
            else:
                for j in range(0, 12):
                    decrypted_password = decrypted_password + chr(encrypted_password[j] ^ xor_pattern_97[j])
        else:
            # Access 2000 or 2002
            for j in range(0, 12):
                if j % 2 == 0:
                    # Every byte with a different sign or encrypt. Encryption signs here for the 0x13
                    t1 = chr(0x13 ^ EncrypFlag ^ encrypted_password[j * 2] ^ xor_pattern_2k[j])
                else:
                    t1 = chr(encrypted_password[j * 2] ^ xor_pattern_2k[j])
                decrypted_password = decrypted_password + t1
        if ord(decrypted_password[1]) < 0x20 or ord(decrypted_password[1]) > 0x7e:
            decrypted_password = ''
        return decrypted_password
