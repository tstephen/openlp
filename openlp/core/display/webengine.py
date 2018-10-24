# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2018 OpenLP Developers                                   #
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
Subclass of QWebEngineView. Adds some special eventhandling needed for screenshots/previews
Heavily inspired by https://stackoverflow.com/questions/33467776/qt-qwebengine-render-after-scrolling/33576100#33576100
"""
import logging

from PyQt5 import QtCore, QtWebEngineWidgets, QtWidgets


LOG_LEVELS = {
    QtWebEngineWidgets.QWebEnginePage.InfoMessageLevel: logging.INFO,
    QtWebEngineWidgets.QWebEnginePage.WarningMessageLevel: logging.WARNING,
    QtWebEngineWidgets.QWebEnginePage.ErrorMessageLevel: logging.ERROR
}


log = logging.getLogger(__name__)


class WebEnginePage(QtWebEngineWidgets.QWebEnginePage):
    """
    A custom WebEngine page to capture Javascript console logging
    """
    def javaScriptConsoleMessage(self, level, message, line_number, source_id):
        """
        Override the parent method in order to log the messages in OpenLP
        """
        log.log(LOG_LEVELS[level], '{source_id}:{line_number} {message}'.format(source_id=source_id,
                                                                                line_number=line_number,
                                                                                message=message))


class WebEngineView(QtWebEngineWidgets.QWebEngineView):
    """
    A sub-classed QWebEngineView to handle paint events of OpenGL
    """
    _child = None  # QtWidgets.QOpenGLWidget
    delegatePaint = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        """
        Constructor
        """
        super(WebEngineView, self).__init__(parent)
        self.setPage(WebEnginePage(self))
        self.settings().setAttribute(QtWebEngineWidgets.QWebEngineSettings.LocalStorageEnabled, True)
        self.settings().setAttribute(QtWebEngineWidgets.QWebEngineSettings.LocalContentCanAccessFileUrls, True)
        self.settings().setAttribute(QtWebEngineWidgets.QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        self.page().settings().setAttribute(QtWebEngineWidgets.QWebEngineSettings.LocalStorageEnabled, True)
        self.page().settings().setAttribute(QtWebEngineWidgets.QWebEngineSettings.LocalContentCanAccessFileUrls, True)
        self.page().settings().setAttribute(QtWebEngineWidgets.QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)

    def eventFilter(self, obj, ev):
        """
        Emit delegatePaint on paint event of the last added QOpenGLWidget child
        """
        if obj == self._child and ev.type() == QtCore.QEvent.Paint:
            self.delegatePaint.emit()
        return super(WebEngineView, self).eventFilter(obj, ev)

    def event(self, ev):
        """
        Handle events
        """
        if ev.type() == QtCore.QEvent.ChildAdded:
            # Only use QOpenGLWidget child
            w = ev.child()
            if w and isinstance(w, QtWidgets.QOpenGLWidget):
                self._child = w
                w.installEventFilter(self)
        return super(WebEngineView, self).event(ev)
