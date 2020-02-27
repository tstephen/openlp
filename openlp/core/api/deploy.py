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
Download and "install" the remote web client
"""
import json
import logging
from zipfile import ZipFile

from openlp.core.common.applocation import AppLocation
from openlp.core.common.httputils import download_file, get_web_page, get_openlp_user_agent

REMOTE_URL = 'https://get.openlp.org/remote/'

log = logging.getLogger(__name__)


def deploy_zipfile(app_root_path, zip_name):
    """
    Process the downloaded zip file and add to the correct directory

    :param str zip_name: the zip file name to be processed
    :param pathlib.Path app_root_path: The directory to expand the zip to

    :return: None
    """
    zip_path = app_root_path / zip_name
    web_zip = ZipFile(zip_path)
    web_zip.extractall(app_root_path)


def download_version_info():
    """
    Download the version information file
    """
    try:
        file_contents = get_web_page(REMOTE_URL + 'version.json', headers={'User-Agent': get_openlp_user_agent()})
    except ConnectionError:
        return False
    if not file_contents:
        return None
    return json.loads(file_contents)


def download_and_check(callback=None):
    """
    Download the web site and deploy it.
    """
    version_info = download_version_info()
    if not version_info:
        log.warning('Unable to access the version information, abandoning download')
        # Show the user an error message
        return None
    file_size = version_info['latest']['size']
    callback.setRange(0, file_size)
    if download_file(callback, REMOTE_URL + '{version}/{filename}'.format(**version_info['latest']),
                     AppLocation.get_section_data_path('remotes') / 'remote.zip'):
        deploy_zipfile(AppLocation.get_section_data_path('remotes'), 'remote.zip')
        return version_info['latest']['version']
    return None
