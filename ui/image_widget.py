from PyQt5.QtWidgets import QLabel, QWidget
from PyQt5.QtGui import QImage, QPixmap

class ImageWidget(QLabel):
    def __init__(self, parent):
        super().__init__(parent)

    def set_image(self, np_image):
        height, width, channel = np_image.shape
        bytesPerLine = 3 * width
        image = QImage(np_image.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()
        self.setPixmap(QPixmap.fromImage(image))