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

import logging
import re

from lxml import etree, objectify

from openlp.core.common import normalize_str
from openlp.core.common.i18n import translate
from openlp.plugins.songs.lib import VerseType
from openlp.plugins.songs.lib.importers.songimport import SongImport
from openlp.plugins.songs.lib.ui import SongStrings

log = logging.getLogger(__name__)


class EasySlidesImport(SongImport):
    """
    Import songs exported from EasySlides

    The format example is here:
    http://wiki.openlp.org/Development:EasySlides_-_Song_Data_Format
    """
    def __init__(self, manager, **kwargs):
        """
        Initialise the class.
        """
        super(EasySlidesImport, self).__init__(manager, **kwargs)

    def do_import(self):
        log.info('Importing EasySlides XML file {source}'.format(source=self.import_source))
        parser = etree.XMLParser(remove_blank_text=True, recover=True)
        try:
            with self.import_source.open('r', encoding='utf-8-sig') as xml_file:
                parsed_file = etree.parse(xml_file, parser)
        except etree.XMLSyntaxError:
            log.exception('XML syntax error in file {name}'.format(name=self.import_source))
            self.log_error(self.import_source, SongStrings().XMLSyntaxError)
            return
        except UnicodeDecodeError:
            log.exception('Unreadable characters in {name}'.format(name=self.import_source))
            self.log_error(self.import_source, SongStrings().XMLSyntaxError)
            return
        file_str = etree.tostring(parsed_file)
        if not file_str:
            log.exception('Could not find XML in file {name}'.format(name=self.import_source))
            self.log_error(self.import_source, SongStrings().XMLSyntaxError)
            return
        xml = file_str.decode()
        song_xml = objectify.fromstring(xml)
        try:
            item_count = len(song_xml.Item)
        except AttributeError:
            log.exception('No root attribute "Item"')
            self.log_error(self.import_source, translate('SongsPlugin.EasySlidesImport',
                                                         'Invalid EasySlides song file. Missing Item tag.'))
            return
        self.import_wizard.progress_bar.setMaximum(item_count)
        for song in song_xml.Item:
            if self.stop_import_flag:
                return
            self._parse_song(song)

    def _parse_song(self, song):
        self._success = True
        self._add_unicode_attribute('title', song.Title1, True)
        if hasattr(song, 'Title2'):
            self._add_unicode_attribute('alternate_title', song.Title2)
        if hasattr(song, 'SongNumber'):
            self._add_unicode_attribute('song_number', song.SongNumber)
        if self.song_number == '0':
            self.song_number = ''
        if hasattr(song, 'Writer'):
            self._add_authors(song.Writer)
        if hasattr(song, 'Copyright'):
            self._add_copyright(song.Copyright)
        if hasattr(song, 'LicenceAdmin1'):
            self._add_copyright(song.LicenceAdmin1)
        if hasattr(song, 'LicenceAdmin2'):
            self._add_copyright(song.LicenceAdmin2)
        if hasattr(song, 'BookReference'):
            self._add_unicode_attribute('song_book_name', song.BookReference)
        self._parse_and_add_lyrics(song)
        if self._success:
            if not self.finish():
                self.log_error(song.Title1 if song.Title1 else '')
        else:
            self.set_defaults()

    def _add_unicode_attribute(self, self_attribute, import_attribute, mandatory=False):
        """
        Add imported values to the song model converting them to unicode at the
        same time. If the unicode decode fails or a mandatory attribute is not
        present _success is set to False so the importer can react
        appropriately.

        :param self_attribute:  The attribute in the song model to populate.
        :param import_attribute: The imported value to convert to unicode and save to the song.
        :param mandatory: Signals that this attribute must exist in a valid song.
        """
        try:
            setattr(self, self_attribute, str(import_attribute).strip())
        except UnicodeDecodeError:
            log.exception('UnicodeDecodeError decoding {attribute}'.format(attribute=import_attribute))
            self._success = False
        except AttributeError:
            log.exception('No attribute {attribute}'.format(attribute=import_attribute))
            if mandatory:
                self._success = False

    def _add_authors(self, writer):
        try:
            self.parse_author(str(writer))
        except UnicodeDecodeError:
            log.exception('Unicode decode error while decoding Writer')
            self._success = False

    def _add_copyright(self, element):
        """
        Add a piece of copyright to the total copyright information for the song.

        :param element: The imported variable to get the data from.
        """
        try:
            self.add_copyright(str(element).strip())
        except UnicodeDecodeError:
            log.exception('Unicode error on decoding copyright: {element}'.format(element=element))
            self._success = False
        except AttributeError:
            pass

    def _parse_and_add_lyrics(self, song):
        """
        Process the song lyrics

        :param song: The song details
        """
        try:
            lyrics = str(song.Contents).strip()
        except UnicodeDecodeError:
            log.exception('Unicode decode error while decoding Contents')
            self._success = False
            return
        except AttributeError:
            log.exception('no Contents')
            self._success = False
            return
        lines = lyrics.split('\n')
        # we go over all lines first, to determine information,
        # which tells us how to parse verses later
        region_lines = {}
        separator_lines = 0
        for line in lines:
            line = line.strip()
            if not line:
                continue
            elif line[1:7] == 'region':
                # this is region separator, probably [region 2]
                region = self._extract_region(line)
                region_lines[region] = 1 + region_lines.get(region, 0)
            elif line[0] == '[':
                separator_lines += 1
        # if the song has separators
        separators = (separator_lines > 0)
        # the number of different regions in song - 1
        if len(region_lines) > 1:
            log.info('EasySlidesImport: the file contained a song named "{title}"'
                     'with more than two regions, but only two regions are tested, '
                     'encountered regions were: {keys}'.format(title=self.title,
                                                               keys=','.join(list(region_lines.keys()))))
        # if the song has regions
        regions = (len(region_lines) > 0)
        # if the regions are inside verses
        regions_in_verses = (regions and region_lines[list(region_lines.keys())[0]] > 1)
        MarkTypes = {
            'CHORUS': VerseType.tags[VerseType.Chorus],
            'VERSE': VerseType.tags[VerseType.Verse],
            'INTRO': VerseType.tags[VerseType.Intro],
            'ENDING': VerseType.tags[VerseType.Ending],
            'BRIDGE': VerseType.tags[VerseType.Bridge],
            'PRECHORUS': VerseType.tags[VerseType.PreChorus]
        }
        verses = {}
        # list as [region, versetype, versenum, instance]
        our_verse_order = []
        default_region = '1'
        reg = default_region
        verses[reg] = {}
        # instance differentiates occurrences of same verse tag
        vt = 'v'
        vn = '1'
        inst = 1
        for line in lines:
            line = line.strip()
            if not line:
                if separators:
                    # separators are used, so empty line means slide break
                    # inside verse
                    if self._list_has(verses, [reg, vt, vn, inst]):
                        inst += 1
                else:
                    # separators are not used, so empty line starts a new verse
                    vt = 'v'
                    vn = len(verses[reg].get(vt, {})) + 1
                    inst = 1
            elif line[0:7] == '[region':
                reg = self._extract_region(line)
                verses.setdefault(reg, {})
                if not regions_in_verses:
                    vt = 'v'
                    vn = '1'
                    inst = 1
            elif line[0] == '[':
                # this is a normal section marker
                marker = line[1:line.find(']')].upper()
                vn = '1'
                # have we got any digits?
                # If so, versenumber is everything from the digits to the end
                match = re.match(r'(.*)(\d+.*)', marker)
                if match:
                    marker = match.group(1).strip()
                    vn = match.group(2)
                vt = MarkTypes.get(marker, 'o') if marker else 'v'
                if regions_in_verses:
                    region = default_region
                inst = 1
                if self._list_has(verses, [reg, vt, vn, inst]):
                    inst = len(verses[reg][vt][vn]) + 1
            else:
                if not [reg, vt, vn, inst] in our_verse_order:
                    our_verse_order.append([reg, vt, vn, inst])
                verses[reg].setdefault(vt, {})
                verses[reg][vt].setdefault(vn, {})
                verses[reg][vt][vn].setdefault(inst, [])
                verses[reg][vt][vn][inst].append(normalize_str(line))
        # done parsing
        versetags = []
        # we use our_verse_order to ensure, we insert lyrics in the same order
        # as these appeared originally in the file
        for [reg, vt, vn, inst] in our_verse_order:
            if self._list_has(verses, [reg, vt, vn, inst]):
                # this is false, but needs user input
                versetag = '{tag}{number}'.format(tag=vt, number=vn)
                versetags.append(versetag)
                lines = '\n'.join(verses[reg][vt][vn][inst])
                self.add_verse(lines, versetag)
        SeqTypes = {
            'p': 'p1',
            'q': 'p2',
            'c': 'c1',
            't': 'c2',
            'b': 'b1',
            'w': 'b2',
            'e': 'e1'}
        # Make use of Sequence data, determining the order of verses
        try:
            order = str(song.Sequence).strip().split(',')
            for tag in order:
                if not tag:
                    continue
                elif tag[0].isdigit():
                    tag = 'v' + tag
                elif tag.lower() in SeqTypes:
                    tag = SeqTypes[tag.lower()]
                else:
                    continue
                if tag in versetags:
                    self.verse_order_list.append(tag)
                else:
                    log.info('Got order item {tag}, which is not in versetags, dropping item from presentation '
                             'order'.format(tag=tag))
        except UnicodeDecodeError:
            log.exception('Unicode decode error while decoding Sequence')
            self._success = False
        except AttributeError:
            pass

    def _list_has(self, lst, sub_items):
        """
        See if the list has sub items

        :param lst: The list to check
        :param sub_items: sub item list
        :return:
        """
        for sub_item in sub_items:
            if sub_item in lst:
                lst = lst[sub_item]
            else:
                return False
        return True

    def _extract_region(self, line):
        # this was true already: line[0:7] == '[region':
        """
        Extract the region from text

        :param line: The line of text
        :return:
        """
        right_bracket = line.find(']')
        return line[7:right_bracket].strip()
