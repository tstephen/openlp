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


class TestLibreOfficeServer(TestCase):
    """
    Test the LibreOfficeServer Class
    """
    def test_constructor(self):
        """
        Test the Constructor from the server
        """
        # GIVEN: No server
        # WHEN: The server object is created
        server = LibreOfficeServer()

        # THEN: The server should have been set up correctly
        self.assertIsNone(server._control)
        self.assertIsNone(server._desktop)
        self.assertIsNone(server._document)
        self.assertIsNone(server._presentation)
        self.assertIsNone(server._process)

    @patch('openlp.plugins.presentations.lib.libreofficeserver.Popen')
    def test_start_process(self, MockedPopen):
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
        self.assertEqual(mocked_process, server._process)

    @patch('openlp.plugins.presentations.lib.libreofficeserver.uno')
    def test_setup_desktop(self, mocked_uno):
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
        self.assertEqual(
            [
                call('uno:pipe,name=openlp_pipe;urp;StarOffice.ComponentContext'),
                call('uno:pipe,name=openlp_pipe;urp;StarOffice.ComponentContext')
            ],
            mocked_resolver.resolve.call_args_list
        )
        MockedServiceManager.createInstanceWithContext.assert_called_once_with(
                'com.sun.star.frame.Desktop', mocked_uno_instance)
        self.assertEqual(MockedServiceManager, server._manager)
        self.assertEqual(mocked_desktop, server._desktop)

    @patch('openlp.plugins.presentations.lib.libreofficeserver.PropertyValue')
    def test_create_property(self, MockedPropertyValue):
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
        self.assertEqual(name, prop.Name)
        self.assertEqual(value, prop.Value)

    def test_get_text_from_page_slide_text(self):
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
        self.assertEqual('Page Text\n', text)

    def test_get_text_from_page_title(self):
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
        self.assertEqual('Page Title\n', text)

    def test_get_text_from_page_notes(self):
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
        self.assertEqual('Page Notes\n', text)

    def test_has_desktop_no_desktop(self):
        """
        Test the has_desktop() method when there's no desktop
        """
        # GIVEN: A LibreOfficeServer object
        server = LibreOfficeServer()

        # WHEN: has_desktop() is called
        result = server.has_desktop()

        # THEN: The result should be False
        self.assertFalse(result)

    def test_has_desktop(self):
        """
        Test the has_desktop() method
        """
        # GIVEN: A LibreOfficeServer object and a desktop
        server = LibreOfficeServer()
        server._desktop = MagicMock()

        # WHEN: has_desktop() is called
        result = server.has_desktop()

        # THEN: The result should be True
        self.assertTrue(result)

    def test_shutdown(self):
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
        self.assertEqual(2, mocked_list.hasMoreElements.call_count)
        mocked_list.nextElement.assert_called_once_with()
        mocked_element_doc.getImplementationName.assert_called_once_with()
        mocked_desktop.terminate.assert_called_once_with()
        server._process.kill.assert_called_once_with()
