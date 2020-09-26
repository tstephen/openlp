# -*- coding: utf-8 -*-

##########################################################################
# OpenLP - Open Source Lyrics Projection                                 #
# ---------------------------------------------------------------------- #
# Copyright (c) 2008-2020 OpenLP Developers                              #
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
This module contains tests for the PdfController
"""
import os
import pytest
from pathlib import Path
from shutil import rmtree
from tempfile import mkdtemp
from unittest import skipIf
from unittest.mock import MagicMock

from PyQt5 import QtCore, QtGui

from openlp.core.common import is_macosx, is_linux, is_win
from openlp.core.display.screens import ScreenList
from openlp.plugins.presentations.lib.pdfcontroller import PdfController, PdfDocument
from tests.utils.constants import RESOURCE_PATH


@pytest.yield_fixture()
def pdf_env(settings, mock_plugin, mocked_qapp):
    temp_folder_path = Path(mkdtemp())
    thumbnail_folder_path = Path(mkdtemp())
    mocked_screen = MagicMock()
    mocked_screen.geometry.return_value = QtCore.QRect(0, 0, 1024, 768)
    mocked_qapp.screens.return_value = [mocked_screen]
    mocked_qapp.primaryScreen = MagicMock()
    mocked_qapp.primaryScreen.return_value = mocked_screen
    ScreenList.create(mocked_qapp)
    yield settings, mock_plugin, temp_folder_path, thumbnail_folder_path
    rmtree(thumbnail_folder_path)
    rmtree(temp_folder_path)


SCREEN = {
    'primary': False,
    'number': 1,
    'size': QtCore.QRect(0, 0, 1024, 768)
}
IS_CI = 'GITLAB_CI' in os.environ or 'APPVEYOR' in os.environ
IS_QT_QPA_PLATFORM_OFFSCREEN = 'QT_QPA_PLATFORM' in os.environ and os.environ['QT_QPA_PLATFORM'] == 'offscreen'


def get_screen_resolution():
    """
    Get the screen resolution
    """
    if is_macosx():
        # Magic numbers... don't ask me why
        return 1024, 768
    elif is_win():
        from win32api import GetSystemMetrics
        return GetSystemMetrics(0), GetSystemMetrics(1)
    elif is_linux():
        if IS_CI:
            return 1024, 768
        else:
            from Xlib.display import Display
            resolution = Display().screen().root.get_geometry()
            return resolution.width, resolution.height
    else:
        return 1024, 768


def test_constructor(settings, mock_plugin):
    """
    Test the Constructor from the PdfController
    """
    # GIVEN: No presentation controller
    controller = None

    # WHEN: The presentation controller object is created
    controller = PdfController(plugin=mock_plugin)

    # THEN: The name of the presentation controller should be correct
    assert 'Pdf' == controller.name, 'The name of the presentation controller should be correct'


def load_pdf(pdf_env):
    """
    Test loading a Pdf using the PdfController
    """
    # GIVEN: A Pdf-file
    test_file_path = RESOURCE_PATH / 'presentations' / 'pdf_test1.pdf'

    # WHEN: The Pdf is loaded
    mock_plugin = pdf_env[1]
    temp_folder_path = pdf_env[2]
    thumbnail_folder_path = pdf_env[3]
    controller = PdfController(plugin=mock_plugin)
    controller.temp_folder = temp_folder_path
    controller.thumbnail_folder = thumbnail_folder_path
    document = PdfDocument(controller, test_file_path)
    loaded = document.load_presentation()

    # THEN: The load should succeed and we should be able to get a pagecount
    assert loaded is True, 'The loading of the PDF should succeed.'
    assert 3 == document.get_slide_count(), 'The pagecount of the PDF should be 3.'


@skipIf(IS_QT_QPA_PLATFORM_OFFSCREEN, 'This test fails when QT_QPA_PLATFORM is set to "offscreen".')
def load_pdf_pictures(pdf_env):
    """
    Test loading a Pdf and check the generated pictures' size
    """
    # GIVEN: A Pdf-file
    test_file_path = RESOURCE_PATH / 'presentations' / 'pdf_test1.pdf'

    # WHEN: The Pdf is loaded
    mock_plugin = pdf_env[1]
    temp_folder_path = pdf_env[2]
    thumbnail_folder_path = pdf_env[3]
    controller = PdfController(plugin=mock_plugin)
    controller.temp_folder = temp_folder_path
    controller.thumbnail_folder = thumbnail_folder_path
    document = PdfDocument(controller, test_file_path)
    loaded = document.load_presentation()

    # THEN: The load should succeed and pictures should be created and have been scaled to fit the screen
    assert loaded is True, 'The loading of the PDF should succeed.'
    image = QtGui.QImage(os.path.join(str(temp_folder_path), 'pdf_test1.pdf', 'mainslide001.png'))
    # Based on the converter used the resolution will differ a bit
    width, height = get_screen_resolution()
    # Calculate the width of the PDF based on the aspect ratio of the PDF
    width = int(round(height * 0.70703125, 0))
    assert image.height() == height, 'The height should be {height}'.format(height=height)
    assert image.width() == width, 'The width should be {width}'.format(width=width)


def test_loading_pdf_using_pymupdf(pdf_env):
    try:
        import fitz  # noqa: F401
    except ImportError:
        pytest.skip('PyMuPDF is not installed')

    load_pdf(pdf_env)
    load_pdf_pictures(pdf_env)
