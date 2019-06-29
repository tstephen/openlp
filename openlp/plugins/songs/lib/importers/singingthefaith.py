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
The :mod:`singingthefaith` module provides the functionality for importing songs which are
exported from Singing The Faith - an Authorised songbook for the Methodist Church of
Great Britain."""


import logging
import re
import os
from pathlib import Path

from openlp.core.common.i18n import translate
from openlp.plugins.songs.lib.importers.songimport import SongImport

log = logging.getLogger(__name__)


class SingingTheFaithImport(SongImport):
    """
    Import songs exported from SingingTheFaith
    """

    hints_available = False
    checks_needed = True
    hintline = {}
    hintfile_version = '0'
    hint_verseOrder = ''
    hint_songtitle = ''
    hint_comments = ''
    hint_ignoreIndent = False


    def do_import(self):
        """
        Receive a single file or a list of files to import.
        """
        if not isinstance(self.import_source, list):
            return
        self.import_wizard.progress_bar.setMaximum(len(self.import_source))
        for file_path in self.import_source:
            if self.stop_import_flag:
                return
            with file_path.open('rt', encoding='cp1251') as song_file:
                self.do_import_file(song_file)

    def do_import_file(self, file):
        """
        Process the SingingTheFaith file - pass in a file-like object, not a file path.
        """
        singingTheFaithVersion = 1
        self.set_defaults()
        # Setup variables
        line_number = 0
        old_indent = 0
        chorus_indent = 5           # It might be 6, but we test for >=
        song_title = 'STF000 -'
        song_number = '0'
        ccli = '0'
        current_verse = ''
        current_verse_type = 'v'
        current_verse_number = 1
        has_chorus = False
        chorus_written = False
        auto_verse_order_ok = False
        verses = []
        author = ''
        copyright = ''
        check_flag = 'z'            # Prepended to title, remove if we think import should be OK

        self.add_comment("Imported with Singing The Faith Importer v "+str(singingTheFaithVersion))

# Get the file_song_number - so we can use it for hints
        filename = Path(file.name)
        song_number_file = filename.stem
        song_number_match = re.search('\d+',song_number_file)
        if song_number_match:
            song_number_file=song_number_match.group()

# See if there are hints available at all
            # See if there is a hints file in the same location as the file
        dir_path = filename.parent
        hints_file_path = dir_path / 'hints.tag'
        try:
            with hints_file_path.open('r') as hints_file:
                hints_available = self.read_hints(hints_file,song_number_file)
        except FileNotFoundError:
            hints_available = False

        try:
            # Read the file
            for line in file:
                line_number += 1

##                print("Read line",line_number,"-",line)

                if hints_available and (str(line_number) in self.hintline):
##                    print("Found hint for line ",line_number)
                    hint = self.hintline[str(line_number)]
##                    print("Hint is ",hint)
                    if hint == "Comment":
                        line.strip()
##                        print("Comment hint for line ",line_number," line is ",line)
                        self.add_comment(line)
                        line_number += 1
                        next(file)
                        continue
                    elif hint == "Ignore":
                        line_number += 1
                        next(file)
                        continue
                    elif hint == "Author":
                        # add as a raw author - do not split and make them a words author
                        line.strip()
                        self.add_author(line,'words')
                        line_number += 1
                        next(file)
                        continue
                    elif hint.startswith("VariantVerse"):
 ##                       print("VariantVerse found - hint is ",hint)
                        (vv,hintverse,replace)=hint.split(" ",2)
                        this_verse = self.verses[int(hintverse)-1]
                        this_verse_str = this_verse[1]
                        new_verse = this_verse_str
                        # There might be multiple replace pairs separated by |
                        replaces=replace.split("|")
                        for rep in replaces:
                            (source_str,dest_str)=rep.split("/")
                            new_verse = new_verse.replace(source_str,dest_str)
                        self.add_verse(new_verse,'v')
                        self.verse_order_list.append('v'+str(current_verse_number))
                        current_verse_number += 1
                        line_number += 1
                        next(file)
                        continue
                    else:
                        self.log_error(translate('SongsPlugin.SingingTheFaithImport', 'File %s' % file.name),
                            translate('SongsPlugin.SingingTheFaithImport', 'Unknown hint %s' % hint))
                    return
                        

                # STF exported lines have a leading verse number at the start of each verse.
                #  remove them - note that we want to track the indent as that shows a chorus
                # so will deal with that before stipping all leading spaces.                
                indent = 0
                if line.strip():
##                    print("Dealing non empty line ",line)
                    verse_num_match = re.search('^\d+',line)
                    if verse_num_match:
                        verse_num = verse_num_match.group()
##                        print("Verse num is ",verse_num)
                        line = line.lstrip("0123456789")
                    indent_match = re.search('^\s+',line)
                    if indent_match:
                       indent=len(indent_match.group())
##                       print("indent is ",indent)

                # Assuming we have sorted out what is verse and what is chorus, strip lines, unless ignoreIndent
                if not self.hint_ignoreIndent:
                    line = line.strip()
                else:
                    line = line.rstrip()
##                print("Read line",line_number,"(",indent,")",line)
                if line_number == 2:
                    # note that songs seem to start with a blank line
                    song_title = line
##                    print("Set song title to "+song_title)
                # Detect the 'Reproduced from Singing the Faith Electronic Words Edition' line
                if line.startswith('Reproduced from Singing the Faith Electronic Words Edition'):
                    song_number_match = re.search('\d+',line)
                    if song_number_match:
                        song_number=song_number_match.group()
##                        print("Found Reproduced - song is ",song_number)
                        continue
                # If the indent is 0 and it contains '(c)' then it is a Copyright line
                elif (indent == 0) and ( "(c)" in line):
                    copyright = line
                    continue
                elif (indent == 0) and (line.startswith('Liturgical ')):
                    self.add_comment(line)
                    continue
                elif (indent == 0) and (line.startswith('From The ')):
                    self.add_comment(line)
                    continue
                elif (indent == 0) and (line.startswith('From Common ')):
                    self.add_comment(line)
                    continue
                # If indent is 0 it may be the author, unless it was one of the cases covered above
                elif (indent == 0) and len(line)>0 :
##                    print ("Possible author ",line)
#                   May have more than one author, separated by ' and '
                    authors = line.split(' and ')
                    for a in authors:
                        self.parse_author(a)
                    continue
                if line == '':
##                    print("Starting a new verse")
                    if current_verse != '':
##                        print("About to add a verse - type ",current_verse_type," ** ",current_verse)
                        self.add_verse(current_verse, current_verse_type)
                        self.verse_order_list.append(current_verse_type+str(current_verse_number))
                        if current_verse_type == 'c':
                            chorus_written = True
                        else:
                            current_verse_number += 1
                    current_verse = ''
                    if chorus_written:
##                        print("Setting current_verse_type to v")
                        current_verse_type = 'v'
                else:
                    # If the line is indented more than or equal chorus_indent then assume it is a chorus
                    # If then indent has just changed then start a new verse just like hitting a blank line

                    if not self.hint_ignoreIndent and ((indent >= chorus_indent) and (old_indent < indent)):
##                        print("Change of indent - close off old verse")
                        if current_verse != '':
##                            print("About to add a verse (indent change) - type ",current_verse_type," ** ",current_verse)
                            self.add_verse(current_verse, current_verse_type)
                            self.verse_order_list.append(current_verse_type+str(current_verse_number))
                            if current_verse_type == 'v':
                                current_verse_number += 1
                        current_verse = line
##                        print("Setting current_verse_type to c");
                        current_verse_type = 'c'
                        old_indent=indent
                        chorus_written = False
                        has_chorus = True
                        continue
                    if current_verse == '':
                        current_verse += line
                    else:
                        current_verse += '\n' + line
                old_indent = indent
        except Exception as e:
            self.log_error(translate('SongsPlugin.SingingTheFaithImport', 'File %s' % file.name),
                           translate('SongsPlugin.SingingTheFaithImport', 'Error: %s') % e)
            return

        if self.hint_songtitle:
            song_title = self.hint_songtitle
        self.title = check_flag+"STF"+song_number.zfill(3)+" - "+song_title
        self.song_book_name="Singing The Faith"
        self.song_number = song_number
        self.ccli_number = ccli
        self.add_copyright(copyright)
# If we have a chorus then the generated Verse order can not be used directly, but we can generate
#  one for two special cases - Verse followed by one chorus (to be repeated after every verse)
#  of Chorus, followed by verses. If hints for ManualCheck or VerseOrder are supplied ignore this
        if has_chorus and not self.hint_verseOrder and not self.checks_needed:
##            print ("Has chorus - verse order list is ",self.verse_order_list)
            auto_verse_order_ok = False
            # Popular case V1 C2 V2 ...
            if len(self.verse_order_list) >= 1:         # protect against odd cases
                if (self.verse_order_list[0] == "v1") and (self.verse_order_list[1] == "c2"):
                    new_verse_order_list = ['v1','c1']
                    i = 2
                    auto_verse_order_ok = True
                elif (self.verse_order_list[0] == "c1") and (self.verse_order_list[1] == "v1"):
                    new_verse_order_list = ['c1','v1','c1']
                    i = 2
                    auto_verse_order_ok = True
                # if we are in a case we can deal with
                if auto_verse_order_ok:
                   while i < len(self.verse_order_list):
                        if self.verse_order_list[i].startswith('v'):
                            new_verse_order_list.append(self.verse_order_list[i])
                            new_verse_order_list.append("c1")
                        else:
                            self.log_error(translate('SongsPlugin.SingingTheFaithImport', 'File %s' % file.name),
                                'Error: Strange verse order entry '+self.verse_order_list[i])
##                            print("Found strange verseorder entry ",self.verse_order_list[i]," in ",file.name)
                            auto_verse_order_ok = False
                        i += 1
##                    print(" new verse_order_list (Chorus first is ",new_verse_order_list)
                   self.verse_order_list = new_verse_order_list 
            else:
                if not auto_verse_order_ok:
                    print ("setting verse_order_list to empty")
                    self.verse_order_list = []
            # If it is a simple case, 
        if self.hint_verseOrder:
            self.verse_order_list = self.hint_verseOrder.split(',')
        if self.hint_comments:
            self.add_comment(self.hint_comments)
# Write the title last as by now we will know if we need checks
        if hints_available and not self.checks_needed:
            check_flag=''
        elif not hints_available and not has_chorus:
            check_flag=''
        elif not hints_available and has_chorus and auto_verse_order_ok:
            check_flag=''
        self.title = check_flag+"STF"+song_number.zfill(3)+" - "+song_title
        if not self.finish():
            self.log_error(file.name)


    def read_hints(self, file, song_number ):
        hintfound = False
#   clear hints
        self.hint_verseOrder = ''
        self.hintline.clear()
        self.hint_comments = ''
        self.hint_songtitle = ''
        self.hint_ignoreIndent = False

##        print("Reading the hints file for ",song_number)
        for tl in file:
#   if the line is empty then return
            if not tl.strip():
                return hintfound
            tagval = tl.split(':')
            tag = tagval[0].strip()
            val = tagval[1].strip()
            if (tag == "Version") :
                self.hintfile_version = val
                continue
            if (tag == "Hymn") and (val == song_number):
##                print ("Found song ",song_number," in hints")
                self.add_comment("Using hints version "+str(self.hintfile_version))
                hintfound = True
#   Assume, unless the hints has ManualCheck that if hinted all will be OK
                self.checks_needed = False
                for tl in file:
                    tagval = tl.split(':')
                    tag = tagval[0].strip()
                    val = tagval[1].strip()
                    if tag == "End":
                        return hintfound
                    elif tag == "CommentsLine":
                        vals = val.split(',')
                        for v in vals:
                            self.hintline[v] = "Comment"
                    elif tag == "IgnoreLine":
                        vals = val.split(',')
                        for v in vals:
                            self.hintline[v] = "Ignore"
                    elif tag == "AuthorLine":
                        vals = val.split(',')
                        for v in vals:
                            self.hintline[v] = "Author"  
                    elif tag == "VerseOrder":
                        self.hint_verseOrder = val
                    elif tag == "ManualCheck":
                        self.checks_needed = True
                    elif tag == "IgnoreIndent":
                        self.hint_ignoreIndent = True
                    elif tag == "VariantVerse":
                        vvline = val.split(' ',1)
                        self.hintline[vvline[0].strip()] = "VariantVerse "+vvline[1].strip()
                    elif tag == "SongTitle":
                        self.hint_songtitle = val
                    elif tag == "AddComment":
                        self.hint_comments += '\n' + val
                    else:
                        print("Unknown tag ",tag," value ",val)



        return hintfound        
 
      
