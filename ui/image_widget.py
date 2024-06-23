from PyQt5.QtWidgets import QLabel, QWidget, QSizePolicy
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtCore import Qt


class ImageWidget(QLabel):

    mouse_down = pyqtSignal(QMouseEvent)
    mouse_up = pyqtSignal(QMouseEvent)
    mouse_move = pyqtSignal(QMouseEvent)

    def __init__(self, parent):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)


    def set_image(self, np_image):
        height, width, channel = np_image.shape
        bytesPerLine = 3 * width
        image = QImage(
            np_image.data, width, height, bytesPerLine, QImage.Format_RGB888
        ).rgbSwapped()
        self.setPixmap(QPixmap.fromImage(image))

    def mousePressEvent(self, event):
        self.mouse_down.emit(event)

    def mouseReleaseEvent(self, event):
        self.mouse_up.emit(event)

    def mouseMoveEvent(self, event):
        self.mouse_move.emit(event)
