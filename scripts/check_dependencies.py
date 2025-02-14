#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##########################################################################
# OpenLP - Open Source Lyrics Projection                                 #
# ---------------------------------------------------------------------- #
# Copyright (c) 2008-2024 OpenLP Developers                              #
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
This script is used to check dependencies of OpenLP. It checks availability
of required python modules and their version. To verify availability of Python
modules, simply run this script::

    $ ./check_dependencies.py

"""
import importlib
import os
import sys
from distutils.version import LooseVersion

IS_WIN = sys.platform.startswith('win')
IS_LIN = sys.platform.startswith('lin')
IS_MAC = sys.platform.startswith('dar')


VERS = {
    'Python': '3.6',
    'PyQt5': '5.12',
    'Qt5': '5.9',
    'pymediainfo': '2.2',
    'sqlalchemy': '0.5',
    'enchant': '1.6'
}

# pywin32
WIN32_MODULES = [
    'win32com',
    'win32ui',
    'pywintypes',
    'icu',
]

LINUX_MODULES = [
    # Optical drive detection.
    'dbus',
    'distro',
]

MACOSX_MODULES = [
    'objc',
    'Pyro5',
    'AppKit'
]


MODULES = [
    'PyQt5',
    'PyQt5.QtCore',
    'PyQt5.QtGui',
    'PyQt5.QtWidgets',
    'PyQt5.QtNetwork',
    'PyQt5.QtOpenGL',
    'PyQt5.QtSvg',
    'PyQt5.QtTest',
    ('PyQt5.QtWebEngineWidgets', '(PyQtWebEngine on PyPI)'),
    'PyQt5.QtMultimedia',
    'platformdirs',
    'sqlalchemy',
    'alembic',
    'lxml',
    'chardet',
    'flask',
    'flask_cors',
    'bs4',
    'mako',
    'websockets',
    'waitress',
    'requests',
    'qtawesome',
    'pymediainfo',
    'vlc',
    'qrcode',
    'packaging',
]


OPTIONAL_MODULES = [
    ('qdarkstyle', '(dark style support)'),
    ('pymysql', '(MySQL support)'),
    ('pyodbc', '(ODBC support)'),
    ('psycopg2', '(PostgreSQL support)'),
    ('enchant', '(spell checker)'),
    ('fitz', '(PyMuPDF - PDF support)'),
    ('pysword', '(import SWORD bibles)'),
    ('uno', '(LibreOffice/OpenOffice support)'),
    # development/testing modules
    ('pytest', '(testing framework)'),
    ('pytestqt', '(PyQt testing framework - pytest-qt on PyPI)'),
    ('flake8', '(linter)')
]

w = sys.stdout.write


def check_vers(version, required, text):
    """
    Check the version of a dependency. Returns ``True`` if the version is greater than or equal, or False if less than.

    ``version``
        The actual version of the dependency

    ``required``
        The required version of the dependency

    ``text``
        The dependency's name
    """
    space = (27 - len(required) - len(text)) * ' '
    if not isinstance(version, str):
        version = '.'.join(map(str, version))
    if not isinstance(required, str):
        required = '.'.join(map(str, required))
    w('  %s >= %s ...  ' % (text, required) + space)
    if LooseVersion(version) >= LooseVersion(required):
        w(version + os.linesep)
        return True
    else:
        w('FAIL' + os.linesep)
        return False


def check_module(mod, text='', indent='  '):
    """
    Check that a module is installed.

    ``mod``
        The module to check for.

    ``text``
        The text to display.

    ``indent``
        How much to indent the text by.
    """
    space = (31 - len(mod) - len(text)) * ' '
    w(indent + '%s %s...  ' % (mod, text) + space)
    try:
        importlib.import_module(mod)
        w('OK')
    except ImportError:
        w('FAIL')
    except Exception:
        w('ERROR')
    w(os.linesep)


def print_vers_fail(required, text):
    print('  %s >= %s ...    FAIL' % (text, required))


def verify_python():
    if not check_vers(list(sys.version_info), VERS['Python'], text='Python'):
        exit(1)


def verify_versions():
    print('Verifying version of modules...')
    try:
        from PyQt5 import QtCore
        check_vers(QtCore.PYQT_VERSION_STR, VERS['PyQt5'], 'PyQt5')
        check_vers(QtCore.qVersion(), VERS['Qt5'], 'Qt5')
    except ImportError:
        print_vers_fail(VERS['PyQt5'], 'PyQt5')
        print_vers_fail(VERS['Qt5'], 'Qt5')
    try:
        import sqlalchemy
        check_vers(sqlalchemy.__version__, VERS['sqlalchemy'], 'sqlalchemy')
    except ImportError:
        print_vers_fail(VERS['sqlalchemy'], 'sqlalchemy')
    try:
        import enchant
        check_vers(enchant.__version__, VERS['enchant'], 'enchant')
    except ImportError:
        print_vers_fail(VERS['enchant'], 'enchant')


def print_enchant_backends_and_languages():
    """
    Check if PyEnchant is installed.
    """
    w('Enchant (spell checker)... ')
    try:
        import enchant
        w(os.linesep)
        backends = ', '.join([x.name for x in enchant.Broker().describe()])
        print('  available backends: %s' % backends)
        langs = ', '.join(enchant.list_languages())
        print('  available languages: %s' % langs)
    except ImportError:
        w('FAIL' + os.linesep)


def print_qt_image_formats():
    """
    Print out the image formats that Qt5 supports.
    """
    w('Qt5 image formats... ')
    try:
        from PyQt5 import QtGui
        read_f = ', '.join([bytes(fmt).decode().lower() for fmt in QtGui.QImageReader.supportedImageFormats()])
        write_f = ', '.join([bytes(fmt).decode().lower() for fmt in QtGui.QImageWriter.supportedImageFormats()])
        w(os.linesep)
        print('  read: %s' % read_f)
        print('  write: %s' % write_f)
    except ImportError:
        w('FAIL' + os.linesep)


def main():
    """
    Run the dependency checker.
    """
    print('Checking Python version...')
    verify_python()
    print('Checking for modules...')
    for m in MODULES:
        if isinstance(m, (tuple, list)):
            check_module(m[0], text=m[1])
        else:
            check_module(m)
    print('Checking for optional modules...')
    for m in OPTIONAL_MODULES:
        check_module(m[0], text=m[1])
    if IS_WIN:
        print('Checking for Windows specific modules...')
        for m in WIN32_MODULES:
            check_module(m)
    elif IS_LIN:
        print('Checking for Linux specific modules...')
        for m in LINUX_MODULES:
            check_module(m)
    elif IS_MAC:
        print('Checking for Mac OS X specific modules...')
        for m in MACOSX_MODULES:
            check_module(m)
    verify_versions()
    print_qt_image_formats()
    print_enchant_backends_and_languages()


if __name__ == '__main__':
    main()
