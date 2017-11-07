# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2017 OpenLP Developers                                   #
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
The :mod:`~openlp.display.render` module contains functions for rendering.
"""
import html
import logging
import math
import re

from openlp.core.lib.formattingtags import FormattingTags

log = logging.getLogger(__name__)

SLIM_CHARS = 'fiíIÍjlĺľrtť.,;/ ()|"\'!:\\'
CHORD_LINE_MATCH = re.compile(r'\[(.*?)\]([\u0080-\uFFFF,\w]*)'
                              '([\u0080-\uFFFF,\w,\s,\.,\,,\!,\?,\;,\:,\|,\",\',\-,\_]*)(\Z)?')
CHORD_TEMPLATE = '<span class="chordline">{chord}</span>'
FIRST_CHORD_TEMPLATE = '<span class="chordline firstchordline">{chord}</span>'
CHORD_LINE_TEMPLATE = '<span class="chord"><span><strong>{chord}</strong></span></span>{tail}{whitespace}{remainder}'
WHITESPACE_TEMPLATE = '<span class="ws">{whitespaces}</span>'


def remove_tags(text, can_remove_chords=False):
    """
    Remove Tags from text for display

    :param text: Text to be cleaned
    :param can_remove_chords: Can we remove the chords too?
    """
    text = text.replace('<br>', '\n')
    text = text.replace('{br}', '\n')
    text = text.replace('&nbsp;', ' ')
    for tag in FormattingTags.get_html_tags():
        text = text.replace(tag['start tag'], '')
        text = text.replace(tag['end tag'], '')
    # Remove ChordPro tags
    if can_remove_chords:
        text = re.sub(r'\[.+?\]', r'', text)
    return text


def has_valid_tags(text):
    """
    The :func:`~openlp.core.display.render.has_valid_tags` function validates the tags within ``text``.

    :param str text: The string with formatting tags in it.
    :returns bool: Returns True if tags are valid, False if there are parsing problems.
    """
    return True


def render_chords_in_line(match):
    """
    Render the chords in the line and align them using whitespaces.
    NOTE: There is equivalent javascript code in chords.js, in the updateSlide function. Make sure to update both!

    :param str match: The line which contains chords
    :returns str: The line with rendered html-chords
    """
    whitespaces = ''
    chord_length = 0
    tail_length = 0
    # The match could be "[G]sweet the " from a line like "A[D]mazing [D7]grace! How [G]sweet the [D]sound!"
    # The actual chord, would be "G" in match "[G]sweet the "
    chord = match.group(1)
    # The tailing word of the chord, would be "sweet" in match "[G]sweet the "
    tail = match.group(2)
    # The remainder of the line, until line end or next chord. Would be " the " in match "[G]sweet the "
    remainder = match.group(3)
    # Line end if found, else None
    end = match.group(4)
    # Based on char width calculate width of chord
    for chord_char in chord:
        if chord_char not in SLIM_CHARS:
            chord_length += 2
        else:
            chord_length += 1
    # Based on char width calculate width of tail
    for tail_char in tail:
        if tail_char not in SLIM_CHARS:
            tail_length += 2
        else:
            tail_length += 1
    # Based on char width calculate width of remainder
    for remainder_char in remainder:
        if remainder_char not in SLIM_CHARS:
            tail_length += 2
        else:
            tail_length += 1
    # If the chord is wider than the tail+remainder and the line goes on, some padding is needed
    if chord_length >= tail_length and end is None:
        # Decide if the padding should be "_" for drawing out words or spaces
        if tail:
            if not remainder:
                for c in range(math.ceil((chord_length - tail_length) / 2) + 2):
                    whitespaces += '_'
            else:
                for c in range(chord_length - tail_length + 1):
                    whitespaces += '&nbsp;'
        else:
            if not remainder:
                for c in range(math.floor((chord_length - tail_length) / 2)):
                    whitespaces += '_'
            else:
                for c in range(chord_length - tail_length + 1):
                    whitespaces += '&nbsp;'
    else:
        if not tail and remainder and remainder[0] == ' ':
            for c in range(chord_length):
                whitespaces += '&nbsp;'
    if whitespaces:
        if '_' in whitespaces:
            ws_length = len(whitespaces)
            if ws_length == 1:
                whitespaces = '&ndash;'
            else:
                wsl_mod = ws_length // 2
                ws_right = ws_left = ' ' * wsl_mod
                whitespaces = ws_left + '&ndash;' + ws_right
        whitespaces = WHITESPACE_TEMPLATE.format(whitespaces=whitespaces)
    return CHORD_LINE_TEMPLATE.format(chord=html.escape(chord), tail=html.escape(tail), whitespace=whitespaces,
                                      remainder=html.escape(remainder))


def render_chords(text):
    """
    Render ChordPro tags

    :param str text: The text containing the chords
    :returns str: The text containing the rendered chords
    """
    text_lines = text.split('{br}')
    rendered_lines = []
    chords_on_prev_line = False
    for line in text_lines:
        # If a ChordPro is detected in the line, replace it with a html-span tag and wrap the line in a span tag.
        if '[' in line and ']' in line:
            if chords_on_prev_line:
                chord_template = CHORD_TEMPLATE
            else:
                chord_template = FIRST_CHORD_TEMPLATE
                chords_on_prev_line = True
            # Matches a chord, a tail, a remainder and a line end. See expand_and_align_chords_in_line() for more info.
            new_line = chord_template.format(chord=CHORD_LINE_MATCH.sub(render_chords_in_line, line))
            rendered_lines.append(new_line)
        else:
            chords_on_prev_line = False
            rendered_lines.append(html.escape(line))
    return '{br}'.join(rendered_lines)


def compare_chord_lyric_width(chord, lyric):
    """
    Compare the width of chord and lyrics. If chord width is greater than the lyric width the diff is returned.

    :param chord:
    :param lyric:
    :return:
    """
    chord_length = 0
    if chord == '&nbsp;':
        return 0
    chord = re.sub(r'\{.*?\}', r'', chord)
    lyric = re.sub(r'\{.*?\}', r'', lyric)
    for chord_char in chord:
        if chord_char not in SLIM_CHARS:
            chord_length += 2
        else:
            chord_length += 1
    lyriclen = 0
    for lyric_char in lyric:
        if lyric_char not in SLIM_CHARS:
            lyriclen += 2
        else:
            lyriclen += 1
    if chord_length > lyriclen:
        return chord_length - lyriclen
    else:
        return 0


def find_formatting_tags(text, active_formatting_tags):
    """
    Look for formatting tags in lyrics and adds/removes them to/from the given list. Returns the update list.

    :param text:
    :param active_formatting_tags:
    :return:
    """
    if not re.search(r'\{.*?\}', text):
        return active_formatting_tags
    word_iterator = iter(text)
    # Loop through lyrics to find any formatting tags
    for char in word_iterator:
        if char == '{':
            tag = ''
            char = next(word_iterator)
            start_tag = True
            if char == '/':
                start_tag = False
                char = next(word_iterator)
            while char != '}':
                tag += char
                char = next(word_iterator)
            # See if the found tag has an end tag
            for formatting_tag in FormattingTags.get_html_tags():
                if formatting_tag['start tag'] == '{' + tag + '}':
                    if formatting_tag['end tag']:
                        if start_tag:
                            # prepend the new tag to the list of active formatting tags
                            active_formatting_tags[:0] = [tag]
                        else:
                            # remove the tag from the list
                            active_formatting_tags.remove(tag)
                    # Break out of the loop matching the found tag against the tag list.
                    break
    return active_formatting_tags


def render_chords_for_printing(text, line_split):
    """
    Render ChordPro tags for printing

    :param str text: The text containing the chords to be rendered.
    :param str line_split: The character(s) used to split lines
    :returns str: The rendered chords
    """
    if not re.search(r'\[.*?\]', text):
        return text
    text_lines = text.split(line_split)
    rendered_text_lines = []
    for line in text_lines:
        # If a ChordPro is detected in the line, build html tables.
        new_line = '<table class="line" width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td>'
        active_formatting_tags = []
        if re.search(r'\[.*?\]', line):
            words = line.split(' ')
            in_chord = False
            for word in words:
                chords = []
                lyrics = []
                new_line += '<table class="segment" cellpadding="0" cellspacing="0" border="0" align="left">'
                # If the word contains a chord, we need to handle it.
                if re.search(r'\[.*?\]', word):
                    chord = ''
                    lyric = ''
                    # Loop over each character of the word
                    for char in word:
                        if char == '[':
                            in_chord = True
                            if lyric != '':
                                if chord == '':
                                    chord = '&nbsp;'
                                chords.append(chord)
                                lyrics.append(lyric)
                                chord = ''
                                lyric = ''
                        elif char == ']' and in_chord:
                            in_chord = False
                        elif in_chord:
                            chord += char
                        else:
                            lyric += char
                    if lyric != '' or chord != '':
                        if chord == '':
                            chord = '&nbsp;'
                        if lyric == '':
                            lyric = '&nbsp;'
                        chords.append(chord)
                        lyrics.append(lyric)
                    new_chord_line = '<tr class="chordrow">'
                    new_lyric_line = '</tr><tr>'
                    for i in range(len(lyrics)):
                        spacer = compare_chord_lyric_width(chords[i], lyrics[i])
                        # Handle formatting tags
                        start_formatting_tags = ''
                        if active_formatting_tags:
                            start_formatting_tags = '{' + '}{'.join(active_formatting_tags) + '}'
                        # Update list of active formatting tags
                        active_formatting_tags = find_formatting_tags(lyrics[i], active_formatting_tags)
                        end_formatting_tags = ''
                        if active_formatting_tags:
                            end_formatting_tags = '{/' + '}{/'.join(active_formatting_tags) + '}'
                        new_chord_line += '<td class="chord">%s</td>' % chords[i]
                        # Check if this is the last column, if so skip spacing calc and instead insert a single space
                        if i + 1 == len(lyrics):
                            new_lyric_line += '<td class="lyrics">{starttags}{lyrics}&nbsp;{endtags}</td>'.format(
                                starttags=start_formatting_tags, lyrics=lyrics[i], endtags=end_formatting_tags)
                        else:
                            spacing = ''
                            if spacer > 0:
                                space = '&nbsp;' * int(math.ceil(spacer / 2))
                                spacing = '<span class="chordspacing">%s-%s</span>' % (space, space)
                            new_lyric_line += '<td class="lyrics">{starttags}{lyrics}{spacing}{endtags}</td>'.format(
                                starttags=start_formatting_tags, lyrics=lyrics[i], spacing=spacing,
                                endtags=end_formatting_tags)
                    new_line += new_chord_line + new_lyric_line + '</tr>'
                else:
                    start_formatting_tags = ''
                    if active_formatting_tags:
                        start_formatting_tags = '{' + '}{'.join(active_formatting_tags) + '}'
                    active_formatting_tags = find_formatting_tags(word, active_formatting_tags)
                    end_formatting_tags = ''
                    if active_formatting_tags:
                        end_formatting_tags = '{/' + '}{/'.join(active_formatting_tags) + '}'
                    new_line += '<tr class="chordrow"><td class="chord">&nbsp;</td></tr><tr><td class="lyrics">' \
                                '{starttags}{lyrics}&nbsp;{endtags}</td></tr>'.format(
                                    starttags=start_formatting_tags, lyrics=word, endtags=end_formatting_tags)
                new_line += '</table>'
        else:
            new_line += line
        new_line += '</td></tr></table>'
        rendered_text_lines.append(new_line)
    # the {br} tag used to split lines is not inserted again since the style of the line-tables makes them redundant.
    return ''.join(rendered_text_lines)


def render_tags(text, can_render_chords=False, is_printing=False):
    """
    The :func:`~openlp.core.display.render.render_tags` function takes a stirng with OpenLP-style tags in it
    and replaces them with the HTML version.

    :param str text: The string with OpenLP-style tags to be rendered.
    :param bool can_render_chords: Should the chords be rendererd?
    :param bool is_printing: Are we going to print this?
    :returns str: The HTML version of the tags is returned as a string.
    """
    if can_render_chords:
        if is_printing:
            text = render_chords_for_printing(text, '{br}')
        else:
            text = render_chords(text)
    for tag in FormattingTags.get_html_tags():
        text = text.replace(tag['start tag'], tag['start html'])
        text = text.replace(tag['end tag'], tag['end html'])
    return text
