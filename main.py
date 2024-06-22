from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QDialog,
    QLabel,
    QWidget
)
import sys
from ui.about_dialog import AboutDialog
from ui.image_widget import ImageWidget

from sympy import Q
from torch import layout

import cv2
import numpy as np

app = QApplication(sys.argv)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt5 App")
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)
        self.menubar = self.menuBar()
        self.create_menu()
        self.image_widget = ImageWidget(self)
        self.layout.addWidget(self.image_widget)
        img = np.zeros((512, 512, 3), np.uint8)
        cv2.circle(img, (50, 50), 20, (255, 0, 0), -1)
        self.image_widget.set_image(img)
        

    def create_menu(self):
        self.file_menu = self.menubar.addMenu("File")
        self.file_menu.addAction("New")
        self.file_menu.addAction("Open")
        self.file_menu.addAction("Save")
        self.file_menu.addAction("Close")
        self.file_menu.addSeparator()
        self.exit_button = self.file_menu.addAction("Exit")
        self.exit_button.triggered.connect(self.close)
        self.help_menu = self.menubar.addMenu("Help")
        self.about_button = self.help_menu.addAction("About")
        self.about_button.triggered.connect(self.show_about_dialog)

    def show_about_dialog(self):
        dialog = AboutDialog(self)
        dialog.setWindowTitle("About")
        dialog.exec_()


window = MainWindow()
window.show()
exit(app.exec_())
