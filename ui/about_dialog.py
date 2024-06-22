from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About")
        self.setGeometry(100, 100, 280, 80)
        
        layout = QVBoxLayout()
        
        about_text = QLabel("Developed by Joji")
        about_text.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(about_text)
        
        self.setLayout(layout)
