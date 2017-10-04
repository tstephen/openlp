import logging
import os
import json

from PyQt5 import QtCore, QtWidgets, QtWebChannel

log = logging.getLogger(__name__)


class MediaWatcher(QtCore.QObject):
    """
    A class to watch media events in the display and emit signals for OpenLP
    """
    progress = QtCore.pyqtSignal(float)
    duration = QtCore.pyqtSignal(float)
    volume = QtCore.pyqtSignal(float)
    playback_rate = QtCore.pyqtSignal(float)
    ended = QtCore.pyqtSignal(bool)
    muted = QtCore.pyqtSignal(bool)

    @QtCore.pyqtSlot(float)
    def update_progress(self, time):
        """
        Notify about the current position of the media
        """
        log.warning(time)
        self.progress.emit(time)

    @QtCore.pyqtSlot(float)
    def update_duration(self, time):
        """
        Notify about the duration of the media
        """
        log.warning(time)
        self.duration.emit(time)

    @QtCore.pyqtSlot(float)
    def update_volume(self, level):
        """
        Notify about the volume of the media
        """
        log.warning(level)
        level = level * 100
        self.volume.emit(level)

    @QtCore.pyqtSlot(float)
    def update_playback_rate(self, rate):
        """
        Notify about the playback rate of the media
        """
        log.warning(rate)
        self.playback_rate.emit(rate)

    @QtCore.pyqtSlot(bool)
    def has_ended(self, is_ended):
        """
        Notify that the media has ended playing
        """
        log.warning(is_ended)
        self.ended.emit(is_ended)

    @QtCore.pyqtSlot(bool)
    def has_muted(self, is_muted):
        """
        Notify that the media has been muted
        """
        log.warning(is_muted)
        self.muted.emit(is_muted)


class DisplayWindow(QtWidgets.QWidget):
    """
    This is a window to show the output
    """
    def __init__(self, parent=None):
        """
        Create the display window
        """
        super(DisplayWindow, self).__init__(parent)
        # Need to import this inline to get around a QtWebEngine issue
        from openlp.core.display.webengine import WebEngineView
        self._is_initialised = False
        self._fbo = None
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Tool | QtCore.Qt.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.webview = WebEngineView(self)
        self.layout.addWidget(self.webview)
        self.webview.loadFinished.connect(self.after_loaded)
        self.set_url(QtCore.QUrl('file://' + os.getcwd() + '/display.html'))
        self.media_watcher = MediaWatcher(self)
        self.channel = QtWebChannel.QWebChannel(self)
        self.channel.registerObject('mediaWatcher', self.media_watcher)
        self.webview.page().setWebChannel(self.channel)

    def set_url(self, url):
        """
        Set the URL of the webview
        """
        if not isinstance(url, QtCore.QUrl):
            url = QtCore.QUrl(url)
        self.webview.setUrl(url)

    def set_html(self, html):
        """
        Set the html
        """
        self.webview.setHtml(html)

    def after_loaded(self):
        """
        Add stuff after page initialisation
        """
        self.run_javascript('Display.init();')

    def run_javascript(self, script, is_sync=False):
        """
        Run some Javascript in the WebView

        :param script: The script to run, a string
        :param is_sync: Run the script synchronously. Defaults to False
        """
        if not is_sync:
            self.webview.page().runJavaScript(script)
        else:
            self.__script_done = False
            self.__script_result = None

            def handle_result(result):
                """
                Handle the result from the asynchronous call
                """
                self.__script_done = True
                self.__script_result = result

            self.webview.page().runJavaScript(script, handle_result)
            while not self.__script_done:
                # TODO: Figure out how to break out of a potentially infinite loop
                QtWidgets.QApplication.instance().processEvents()
            return self.__script_result

    def set_verses(self, verses):
        """
        Set verses in the display
        """
        json_verses = json.dumps(verses)
        self.run_javascript('Display.setTextSlides({verses});'.format(verses=json_verses))

    def set_images(self, images):
        """
        Set images in the display
        """
        for image in images:
            if not image['file'].startswith('file://'):
                image['file'] = 'file://' + image['file']
        json_images = json.dumps(images)
        self.run_javascript('Display.setImageSlides({images});'.format(images=json_images))

    def set_video(self, video):
        """
        Set video in the display
        """
        if not video['file'].startswith('file://'):
            video['file'] = 'file://' + video['file']
        json_video = json.dumps(video)
        self.run_javascript('Display.setVideo({video});'.format(video=json_video))

    def play_video(self):
        """
        Play the currently loaded video
        """
        self.run_javascript('Display.playVideo();')

    def pause_video(self):
        """
        Pause the currently playing video
        """
        self.run_javascript('Display.pauseVideo();')

    def stop_video(self):
        """
        Stop the currently playing video
        """
        self.run_javascript('Display.stopVideo();')

    def set_video_playback_rate(self, rate):
        """
        Set the playback rate of the current video.

        The rate can be any valid float, with 0.0 being stopped, 1.0 being normal speed,
        over 1.0 is faster, under 1.0 is slower, and negative is backwards.

        :param rate: A float indicating the playback rate.
        """
        self.run_javascript('Display.setPlaybackRate({rate});'.format(rate))

    def set_video_volume(self, level):
        """
        Set the volume of the current video.

        The volume should be an int from 0 to 100, where 0 is no sound and 100 is maximum volume. Any
        values outside this range will raise a ``ValueError``.

        :param level: A number between 0 and 100
        """
        if level < 0 or level > 100:
            raise ValueError('Volume should be from 0 to 100, was "{}"'.format(level))
        self.run_javascript('Display.setVideoVolume({level});'.format(level))

    def toggle_video_mute(self):
        """
        Toggle the mute of the current video
        """
        self.run_javascript('Display.toggleVideoMute();')

    def save_screenshot(self, fname=None):
        """
        Save a screenshot, either returning it or saving it to file
        """
        pixmap = self.grab()
        if fname:
            ext = os.path.splitext(fname)[-1][1:]
            pixmap.save(fname, ext)
        else:
            return pixmap

    def set_theme(self, theme):
        """
        Set the theme of the display
        """
        print(theme.export_theme())
        self.run_javascript('Display.setTheme({theme});'.format(theme=theme.export_theme()))
