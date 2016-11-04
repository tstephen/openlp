# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2016 OpenLP Developers                                   #
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
Functional tests to test the LibreOffice Pyro server
"""
from unittest import TestCase

from openlp.plugins.presentations.lib.libreofficeserver import LibreOfficeServer, TextType

from tests.functional import MagicMock, patch, call


def test_constructor():
    """
    Test the Constructor from the server
    """
    # GIVEN: No server
    # WHEN: The server object is created
    server = LibreOfficeServer()

    # THEN: The server should have been set up correctly
    assert server._control is None
    assert server._desktop is None
    assert server._document is None
    assert server._presentation is None
    assert server._process is None

@patch('openlp.plugins.presentations.lib.libreofficeserver.Popen')
def test_start_process(MockedPopen):
    """
    Test that the correct command is issued to run LibreOffice
    """
    # GIVEN: A LOServer
    mocked_process = MagicMock()
    MockedPopen.return_value = mocked_process
    server = LibreOfficeServer()

    # WHEN: The start_process() method is run
    server.start_process()

    # THEN: The correct command line should run and the process should have started
    MockedPopen.assert_called_with([
        '/Applications/LibreOffice.app/Contents/MacOS/soffice',
        '--nologo',
        '--norestore',
        '--minimized',
        '--nodefault',
        '--nofirststartwizard',
        '--accept=pipe,name=openlp_pipe;urp;'
    ])
    assert server._process is mocked_process

@patch('openlp.plugins.presentations.lib.libreofficeserver.uno')
def test_setup_desktop(mocked_uno):
    """
    Test that setting up the desktop works correctly
    """
    # GIVEN: A LibreOfficeServer instance
    server = LibreOfficeServer()
    mocked_context = MagicMock()
    mocked_resolver = MagicMock()
    mocked_uno_instance = MagicMock()
    MockedServiceManager = MagicMock()
    mocked_desktop = MagicMock()
    mocked_uno.getComponentContext.return_value = mocked_context
    mocked_context.ServiceManager.createInstanceWithContext.return_value = mocked_resolver
    mocked_resolver.resolve.side_effect = [Exception, mocked_uno_instance]
    mocked_uno_instance.ServiceManager = MockedServiceManager
    MockedServiceManager.createInstanceWithContext.return_value = mocked_desktop

    # WHEN: setup_desktop() is called
    server.setup_desktop()

    # THEN: A desktop object was created
    mocked_uno.getComponentContext.assert_called_once_with()
    mocked_context.ServiceManager.createInstanceWithContext.assert_called_once_with(
            'com.sun.star.bridge.UnoUrlResolver', mocked_context)
    expected_calls = [
        call('uno:pipe,name=openlp_pipe;urp;StarOffice.ComponentContext'),
        call('uno:pipe,name=openlp_pipe;urp;StarOffice.ComponentContext')
    ]
    assert mocked_resolver.resolve.call_args_list == expected_calls
    MockedServiceManager.createInstanceWithContext.assert_called_once_with(
            'com.sun.star.frame.Desktop', mocked_uno_instance)
    assert server._manager is MockedServiceManager
    assert server._desktop is mocked_desktop

@patch('openlp.plugins.presentations.lib.libreofficeserver.PropertyValue')
def test_create_property(MockedPropertyValue):
    """
    Test that the _create_property() method works correctly
    """
    # GIVEN: A server amnd property to set
    server = LibreOfficeServer()
    name = 'Hidden'
    value = True

    # WHEN: The _create_property() method is called
    prop = server._create_property(name, value)

    # THEN: The property should have the correct attributes
    assert prop.Name == name
    assert prop.Value == value

def test_get_text_from_page_slide_text():
    """
    Test that the _get_text_from_page() method gives us nothing for slide text
    """
    # GIVEN: A LibreOfficeServer object and some mocked objects
    text_type = TextType.SlideText
    slide_no = 1
    server = LibreOfficeServer()
    server._document = MagicMock()
    mocked_pages = MagicMock()
    mocked_page = MagicMock()
    mocked_shape = MagicMock()
    server._document.getDrawPages.return_value = mocked_pages
    mocked_pages.getCount.return_value = 1
    mocked_pages.getByIndex.return_value = mocked_page
    mocked_page.getByIndex.return_value = mocked_shape
    mocked_shape.getShapeType.return_value = 'com.sun.star.presentation.TitleTextShape'
    mocked_shape.supportsService.return_value = True
    mocked_shape.getString.return_value = 'Page Text'

    # WHEN: _get_text_from_page() is run for slide text
    text = server._get_text_from_page(slide_no, text_type)

    # THE: The text is correct
    assert text == 'Page Text\n'

def test_get_text_from_page_title():
    """
    Test that the _get_text_from_page() method gives us the text from the titles
    """
    # GIVEN: A LibreOfficeServer object and some mocked objects
    text_type = TextType.Title
    slide_no = 1
    server = LibreOfficeServer()
    server._document = MagicMock()
    mocked_pages = MagicMock()
    mocked_page = MagicMock()
    mocked_shape = MagicMock()
    server._document.getDrawPages.return_value = mocked_pages
    mocked_pages.getCount.return_value = 1
    mocked_pages.getByIndex.return_value = mocked_page
    mocked_page.getByIndex.return_value = mocked_shape
    mocked_shape.getShapeType.return_value = 'com.sun.star.presentation.TitleTextShape'
    mocked_shape.supportsService.return_value = True
    mocked_shape.getString.return_value = 'Page Title'

    # WHEN: _get_text_from_page() is run for titles
    text = server._get_text_from_page(slide_no, text_type)

    # THEN: The text should be correct
    assert text == 'Page Title\n'

def test_get_text_from_page_notes():
    """
    Test that the _get_text_from_page() method gives us the text from the notes
    """
    # GIVEN: A LibreOfficeServer object and some mocked objects
    text_type = TextType.Notes
    slide_no = 1
    server = LibreOfficeServer()
    server._document = MagicMock()
    mocked_pages = MagicMock()
    mocked_page = MagicMock()
    mocked_notes_page = MagicMock()
    mocked_shape = MagicMock()
    server._document.getDrawPages.return_value = mocked_pages
    mocked_pages.getCount.return_value = 1
    mocked_pages.getByIndex.return_value = mocked_page
    mocked_page.getNotesPage.return_value = mocked_notes_page
    mocked_notes_page.getByIndex.return_value = mocked_shape
    mocked_shape.getShapeType.return_value = 'com.sun.star.presentation.TitleTextShape'
    mocked_shape.supportsService.return_value = True
    mocked_shape.getString.return_value = 'Page Notes'

    # WHEN: _get_text_from_page() is run for titles
    text = server._get_text_from_page(slide_no, text_type)

    # THEN: The text should be correct
    assert text == 'Page Notes\n'

def test_has_desktop_no_desktop():
    """
    Test the has_desktop() method when there's no desktop
    """
    # GIVEN: A LibreOfficeServer object
    server = LibreOfficeServer()

    # WHEN: has_desktop() is called
    result = server.has_desktop()

    # THEN: The result should be False
    assert result is False

def test_has_desktop():
    """
    Test the has_desktop() method
    """
    # GIVEN: A LibreOfficeServer object and a desktop
    server = LibreOfficeServer()
    server._desktop = MagicMock()

    # WHEN: has_desktop() is called
    result = server.has_desktop()

    # THEN: The result should be True
    assert result is True

def test_shutdown():
    """
    Test the shutdown method
    """
    # GIVEN: An up an running LibreOfficeServer
    server = LibreOfficeServer()
    mocked_doc = MagicMock()
    mocked_desktop = MagicMock()
    mocked_docs = MagicMock()
    mocked_list = MagicMock()
    mocked_element_doc = MagicMock()
    server._docs = [mocked_doc]
    server._desktop = mocked_desktop
    server._process = MagicMock()
    def close_docs():
        server._docs = []
    mocked_doc.close_presentation.side_effect = close_docs
    mocked_desktop.getComponents.return_value = mocked_docs
    mocked_docs.hasElements.return_value = True
    mocked_docs.createEnumeration.return_value = mocked_list
    mocked_list.hasMoreElements.side_effect = [True, False]
    mocked_list.nextElement.return_value = mocked_element_doc
    mocked_element_doc.getImplementationName.return_value = 'com.sun.star.comp.framework.BackingComp'

    # WHEN: shutdown() is called
    server.shutdown()

    # THEN: The right methods are called and everything works
    mocked_doc.close_presentation.assert_called_once_with()
    mocked_desktop.getComponents.assert_called_once_with()
    mocked_docs.hasElements.assert_called_once_with()
    mocked_docs.createEnumeration.assert_called_once_with()
    assert mocked_list.hasMoreElements.call_count == 2
    mocked_list.nextElement.assert_called_once_with()
    mocked_element_doc.getImplementationName.assert_called_once_with()
    mocked_desktop.terminate.assert_called_once_with()
    server._process.kill.assert_called_once_with()

@patch('openlp.plugins.presentations.lib.libreofficeserver.uno')
def test_load_presentation(mocked_uno):
    """
    Test the load_presentation() method
    """
    # GIVEN: A LibreOfficeServer object
    presentation_file = '/path/to/presentation.odp'
    screen_number = 1
    server = LibreOfficeServer()
    mocked_desktop = MagicMock()
    mocked_document = MagicMock()
    mocked_presentation = MagicMock()
    mocked_uno.systemPathToFileUrl.side_effect = lambda x: x
    server._desktop = mocked_desktop
    mocked_desktop.loadComponentFromURL.return_value = mocked_document
    mocked_document.getPresentation.return_value = mocked_presentation

    # WHEN: load_presentation() is called
    with patch.object(server, '_create_property') as mocked_create_property:
        mocked_create_property.side_effect = lambda x, y: {x: y}
        result = server.load_presentation(presentation_file, screen_number)

    # THEN: A presentation is loaded
    assert result is True
    mocked_uno.systemPathToFileUrl.assert_called_once_with(presentation_file)
    mocked_create_property.assert_called_once_with('Hidden', True)
    mocked_desktop.loadComponentFromURL.assert_called_once_with(
        presentation_file, '_blank', 0, ({'Hidden': True},))
    assert server._document is mocked_document
    mocked_document.getPresentation.assert_called_once_with()
    assert server._presentation is mocked_presentation
    assert server._presentation.Display == screen_number
    assert server._control is None

@patch('openlp.plugins.presentations.lib.libreofficeserver.uno')
@patch('openlp.plugins.presentations.lib.libreofficeserver.os')
def test_extract_thumbnails(mocked_os, mocked_uno):
    """
    Test the extract_thumbnails() method
    """
    # GIVEN: A LibreOfficeServer instance
    temp_folder = '/tmp'
    server = LibreOfficeServer()
    mocked_document = MagicMock()
    mocked_pages = MagicMock()
    mocked_page_1 = MagicMock()
    mocked_page_2 = MagicMock()
    mocked_controller = MagicMock()
    server._document = mocked_document
    mocked_uno.systemPathToFileUrl.side_effect = lambda x: x
    mocked_document.getDrawPages.return_value = mocked_pages
    mocked_os.path.isdir.return_value = False
    mocked_pages.getCount.return_value = 2
    mocked_pages.getByIndex.side_effect = [mocked_page_1, mocked_page_2]
    mocked_document.getCurrentController.return_value = mocked_controller
    mocked_os.path.join.side_effect = lambda *x: '/'.join(x)

    # WHEN: The extract_thumbnails() method is called
    with patch.object(server, '_create_property') as mocked_create_property:
        mocked_create_property.side_effect = lambda x, y: {x: y}
        thumbnails = server.extract_thumbnails(temp_folder)

    # THEN: Thumbnails have been extracted
    mocked_uno.systemPathToFileUrl.assert_called_once_with(temp_folder)
    mocked_create_property.assert_called_once_with('FilterName', 'impress_png_Export')
    mocked_document.getDrawPages.assert_called_once_with()
    mocked_pages.getCount.assert_called_once_with()
    assert mocked_pages.getByIndex.call_args_list == [call(0), call(1)]
    assert mocked_controller.setCurrentPage.call_args_list == \
        [call(mocked_page_1), call(mocked_page_2)]
    assert mocked_document.storeToURL.call_args_list == \
        [call('/tmp/1.png', ({'FilterName': 'impress_png_Export'},)),
         call('/tmp/2.png', ({'FilterName': 'impress_png_Export'},))]
    assert thumbnails == ['/tmp/1.png', '/tmp/2.png']
