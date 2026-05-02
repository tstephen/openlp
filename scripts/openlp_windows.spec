# -*- mode: python ; coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

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
"""PyInstaller spec for building OpenLP as a Windows one-folder bundle."""

import os
from PyInstaller.utils.hooks import collect_dynamic_libs, collect_submodules

ROOT = os.path.abspath(os.path.join(SPECPATH, '..'))
pyside_binaries = collect_dynamic_libs('PySide6')
chardet_pipeline_hiddenimports = collect_submodules('chardet.pipeline')

a = Analysis(
    [os.path.join(ROOT, 'openlp', '__main__.py')],
    pathex=[ROOT],
    binaries=pyside_binaries,
    datas=[
        (os.path.join(ROOT, 'openlp', 'core', 'display', 'html'), 'openlp/core/display/html'),
        (os.path.join(ROOT, 'openlp', 'core', 'ui', 'fonts'), 'openlp/core/ui/fonts'),
        (os.path.join(ROOT, 'openlp', 'core', 'resources.py'), 'openlp/core'),
        (os.path.join(ROOT, 'resources', 'i18n'), 'resources/i18n'),
        (os.path.join(ROOT, 'resources', 'images'), 'resources/images'),
        (os.path.join(ROOT, 'resources', 'forms'), 'resources/forms'),
    ],
    hiddenimports=[
        'chardet',
        'chardet.universaldetector',
        *chardet_pipeline_hiddenimports,
        'openlp.plugins.alerts',
        'openlp.plugins.alerts.alertsplugin',
        'openlp.plugins.bibles',
        'openlp.plugins.bibles.bibleplugin',
        'openlp.plugins.custom',
        'openlp.plugins.custom.customplugin',
        'openlp.plugins.images',
        'openlp.plugins.images.imagesplugin',
        'openlp.plugins.media',
        'openlp.plugins.media.mediaplugin',
        'openlp.plugins.obs_studio',
        'openlp.plugins.obs_studio.obs_studio_plugin',
        'openlp.plugins.planningcenter',
        'openlp.plugins.planningcenter.planningcenterplugin',
        'openlp.plugins.presentations',
        'openlp.plugins.presentations.presentationplugin',
        'openlp.plugins.songs',
        'openlp.plugins.songs.songsplugin',
        'openlp.plugins.songusage',
        'openlp.plugins.songusage.songusageplugin',
        'sqlalchemy.dialects.sqlite',
        'sqlalchemy.dialects.mysql',
        'sqlalchemy.dialects.postgresql',
        'win32api',
        'win32con',
        'win32gui',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'distro',
        'Pyro5',
        'pyobjc',
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='OpenLP',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    icon=os.path.join(ROOT, 'resources', 'images', 'OpenLP.ico'),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name='OpenLP',
)
