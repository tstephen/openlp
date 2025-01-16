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
The :mod:`~openlp.core.widgets.comboboxes` module contains customized versions of the QComboBox widget
"""
from typing import Callable

from PySide6 import QtWidgets


class LazyComboBox(QtWidgets.QComboBox):
    """
    Custom QComboBox that can lazily load items when user clicks the combo box.
    """

    def __init__(self, parent, loader: Callable[[], bool]):
        """
        Initialize

        :param parent: The parent of this widget.
        :param loader: The function called when the user clicks the combo box. This
            function should return True if load was successful, or False if not.
        """

        super().__init__(parent)

        self.loader = loader
        self.loaded = False

    def showPopup(self):
        """Called right before the popup is shown"""

        if not self.loaded:
            self.loaded = self.loader()

        super().showPopup()
