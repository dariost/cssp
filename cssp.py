#!/usr/bin/env python3

# Copyright 2016 - Dario Ostuni <another.code.996@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import vlc
import json
from random import randint, randrange
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication
from PyQt5.QtCore import QCoreApplication, Qt, QTimer
from PyQt5 import QtGui

class MainWindow(QWidget):
    def __init__(self):
        global settings
        super().__init__()
        self.initGUI()
        self._playing = False
        self.player_instance = vlc.Instance()
        self.player = self.player_instance.media_player_new()
        self.player_volume = int(settings["audio_volume"])
        self._timer = QTimer()
        self._timer.timeout.connect(self.timer_action)
        self._timer.start(int(images["playing_animation_delay_ms"]))
        self.img_index = 0
    def timer_action(self):
        global images
        if self._playing:
            if self.player.is_playing() == 0:
                self._playing = False
                self.img_index = 0
                self.setMask(self.img_default.mask())
                self.palette.setBrush(QtGui.QPalette.Background, QtGui.QBrush(self.img_default))
                self.setPalette(self.palette)
            else:
                if images["playing_animation_rand_perc"] > randint(0, 100):
                    self.setMask(self.img_vector[self.img_index % len(self.img_vector)].mask())
                    self.palette.setBrush(QtGui.QPalette.Background, QtGui.QBrush(self.img_vector[self.img_index % len(self.img_vector)]))
                    if images["playing_animation_randomize"]:
                        self.img_index = randrange(0, len(self.img_vector))
                    else:
                        self.img_index += 1
                    self.setPalette(self.palette)
    def initGUI(self):
        global images, settings
        self.img_default = QtGui.QPixmap(settings["theme_folder"] + "/" + images["default"])
        self.img_vector = []
        for imgname in images["playing"]:
            self.img_vector.append(QtGui.QPixmap(settings["theme_folder"] + "/" + imgname))
        self.setWindowFlags(Qt.Widget | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        #self.setAttribute(Qt.WA_NoSystemBackground, True)
        #self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_OpaquePaintEvent, False)
        self.resize(self.img_default.width(), self.img_default.height())
        self.palette = QtGui.QPalette()
        self.palette.setBrush(QtGui.QPalette.Base, Qt.transparent)
        self.palette.setBrush(QtGui.QPalette.Background, QtGui.QBrush(self.img_default))
        self.setPalette(self.palette)
        self.setMask(self.img_default.mask())
        self.setAcceptDrops(True)
        self.show()
    def wheelEvent(self, event):
        global settings
        self.player_volume += event.angleDelta().y() / 12 * float(settings["wheel_speed"])
        self.player_volume = max(self.player_volume, 0)
        self.player_volume = min(self.player_volume, 200)
        self.player.audio_set_volume(int(self.player_volume))
    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            QCoreApplication.instance().quit()
        elif event.button() == Qt.LeftButton:
            self._offset = event.pos()
        elif event.button() == Qt.MiddleButton:
            self.player.stop()
            self._playing = False
            self.img_index = 0
            self.setMask(self.img_default.mask())
            self.palette.setBrush(QtGui.QPalette.Background, QtGui.QBrush(self.img_default))
            self.setPalette(self.palette)
    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.move(self.mapToParent(event.pos() - self._offset))
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    def dropEvent(self, event):
        self.player.stop()
        self.track = self.player_instance.media_new(event.mimeData().urls()[0].toLocalFile())
        self.player.set_media(self.track)
        self.player.play()
        self._playing = True

if __name__ == "__main__":
    global images, theme_folder
    if "--help" in sys.argv or "--version" in sys.argv:
        print("Cute Side-Screen Player version 0.0.2")
        print("License: GPL3+")
        print("Copyright 2016 - Dario Ostuni <another.code.996@gmail.com>")
        sys.exit(0)
    settings = json.loads(open("settings.json", "r").read())
    images = json.loads(open(settings["theme_folder"] + "/theme.json", "r").read())
    app = QApplication(sys.argv)
    win = MainWindow()
    sys.exit(app.exec_())
