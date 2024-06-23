from math import inf
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QDialog,
    QLabel,
    QWidget,
    QAction,
    QActionGroup,
    QMessageBox,
    QFileDialog,
    # QObject
)
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtCore import pyqtSignal, QObject

import sys
import os

from ui.about_dialog import AboutDialog
from ui.image_widget import ImageWidget


import cv2
import numpy as np

from ui.tools import FloodFillTool, FreehandTool, LineTool

app = QApplication(sys.argv)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Paint")
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)
        self.menubar = self.menuBar()
        self.create_menu()
        self.image_widget = ImageWidget(self)
        self.image_widget.mouse_down.connect(self.mouse_down_event)
        self.image_widget.mouse_up.connect(self.mouse_up_event)
        self.image_widget.mouse_move.connect(self.mouse_move_event)
        self.layout.addWidget(self.image_widget)
        img = np.ones((512, 512, 3), np.uint8) * 255
        self.img = img
        self.image_widget.set_image(img)

        self.ctx = {
            "img": self.img,
            "undo_stack": [],
            "redo_stack": [],
            "tool": None,
            "color": (0, 0, 0),
        }

        self.tool = FreehandTool(img, self.ctx)
        self.tool.committed.connect(self.on_tool_committed)
        self.undo_stack = []
        self.redo_stack = []

    def on_tool_committed(self, command):
        self.undo_stack.append(command)
        self.redo_stack = []
        self.image_widget.set_image(self.img)

    def new_file(self):
        if self.undo_stack:
            reply = QMessageBox.question(
                self,
                "Confirmation",
                "You have unsaved changes. Are you sure you want to start a new file?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                self.img = np.ones((512, 512, 3), np.uint8) * 255
                self.tool = FreehandTool(self.img, self.ctx)
                self.undo_stack.clear()
                print("New file created, undo stack cleared.")
            else:
                print("New file action cancelled.")
        else:
            self.img = np.ones((512, 512, 3), np.uint8) * 255
            self.tool.committed.disconnect(self.on_tool_committed)
            del self.tool
            self.tool = FreehandTool(self.img, self.ctx)
            self.tool.committed.connect(self.on_tool_committed)
        self.image_widget.set_image(self.img)

    def create_menu(self):

        self.create_file_menu()
        self.create_edit_menu()
        self.create_tools_menu()
        self.create_colors_menu()
        self.create_help_menu()

    def create_file_menu(self):
        self.file_menu = self.menubar.addMenu("File")
        new_file_action = QAction("New", self)
        new_file_action.setShortcut(QKeySequence.New)
        new_file_action.triggered.connect(self.new_file)
        self.file_menu.addAction(new_file_action)

        # Open Action
        open_action = QAction("Open", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_image_dialog)
        self.file_menu.addAction(open_action)

        save_action = QAction("Save", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.save_image_dialog)
        self.file_menu.addAction(save_action)
        self.file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        self.file_menu.addAction(exit_action)

    def create_edit_menu(self):

        self.edit_menu = self.menubar.addMenu("Edit")
        self.undo_stack = []
        undoAction = QAction("Undo", self)
        undoAction.setShortcut(QKeySequence.Undo)
        redoAction = QAction("Redo", self)
        redoAction.setShortcut(QKeySequence.Redo)
        redoAction.triggered.connect(self.redo)
        self.redo_button = self.edit_menu.addAction(redoAction)
        self.undo_button = self.edit_menu.addAction(undoAction)
        undoAction.triggered.connect(self.undo)

    def create_tools_menu(self):
        self.tools_menu = self.menubar.addMenu("Tools")
        self.toolActionGroup = QActionGroup(self, exclusive=True)
        for tool_name in ["Freehand", "Line", "Flood Fill"]:
            action = QAction(tool_name, self, checkable=True)
            self.toolActionGroup.addAction(action)

            self.tools_menu.addAction(action)

        self.toolActionGroup.triggered.connect(self.tool_selected)

        self.toolActionGroup.actions()[0].setChecked(True)

    def create_colors_menu(self):
        colors = {
            "Black": (0, 0, 0),
            "White": (255, 255, 255),
            "Red": (255, 0, 0),
            "Green": (0, 255, 0),
            "Blue": (0, 0, 255),
            "Yellow": (255, 255, 0),
            "Cyan": (0, 255, 255),
            "Magenta": (255, 0, 255),
        }

        self.color_menu = self.menubar.addMenu("Color")
        self.colorActionGroup = QActionGroup(self, exclusive=True)
        for color in colors:
            action = QAction(color, self, checkable=True)
            self.colorActionGroup.addAction(action)
            self.color_menu.addAction(action)
        self.colorActionGroup.triggered.connect(self.color_selected)
        self.colorActionGroup.actions()[0].setChecked(True)

    def create_help_menu(self):
        self.help_menu = self.menubar.addMenu("Help")
        self.about_button = self.help_menu.addAction("About")
        self.about_button.triggered.connect(self.show_about_dialog)

    def color_selected(self, action):
        color = action.text()
        colors = {
            "Black": (0, 0, 0),
            "White": (255, 255, 255),
            "Red": (255, 0, 0),
            "Green": (0, 255, 0),
            "Blue": (0, 0, 255),
            "Yellow": (255, 255, 0),
            "Cyan": (0, 255, 255),
            "Magenta": (255, 0, 255),
        }
        self.ctx["color"] = colors[color]

    def open_image_dialog(self):
        if self.undo_stack:
            reply = QMessageBox.question(
                self,
                "Confirmation",
                "You have unsaved changes. Are you sure you want to open a new file?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply == QMessageBox.No:
                print("Open file action cancelled.")
                return
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        # Set up file filters to only show images
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Open Image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)",
            options=options,
        )
        if file_name:
            self.img = cv2.imread(file_name)
            self.image_widget.set_image(self.img)
            self.undo_stack.clear()
            self.redo_stack.clear()
            self.tool.committed.disconnect(self.on_tool_committed)
            del self.tool
            self.tool = FreehandTool(self.img, self.ctx)
            self.tool.committed.connect(self.on_tool_committed)

        else:
            print("No file selected.")

    def save_image_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Save Image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)",
            options=options,
        )
        # Check if the file exists
        if os.path.exists(file_name):
            reply = QMessageBox.question(
                self,
                "Confirmation",
                "The file already exists. Do you want to overwrite it?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply == QMessageBox.No:
                print("Save file action cancelled.")
                return
        if file_name:
            cv2.imwrite(file_name, self.img)
            print("Image saved to:", file_name)
        else:
            print("No file selected.")

    def tool_selected(self, action):
        action_dict = {
            "Line": LineTool,
            "Freehand": FreehandTool,
            "Flood Fill": FloodFillTool,
        }
        tool_class = action_dict[action.text()]
        self.set_tool(tool_class)
        if self.tool is not None:
            self.tool.committed.disconnect(self.on_tool_committed)
            del self.tool
        self.tool = action_dict[action.text()](self.img, self.ctx)
        self.tool.committed.connect(self.on_tool_committed)

    def undo(self):
        if len(self.undo_stack) > 0:
            command = self.undo_stack.pop()
            self.redo_stack.append(command)
            command.undo()
        self.image_widget.set_image(self.img)

    def redo(self):
        if len(self.redo_stack) > 0:
            command = self.redo_stack.pop()
            self.undo_stack.append(command)
            command.execute()
        self.image_widget.set_image(self.img)

    def set_tool(self, tool_class):
        if self.tool:
            self.tool.committed.disconnect(self.on_tool_committed)
            del self.tool
        self.tool = tool_class(self.img, self.ctx)
        self.tool.committed.connect(self.on_tool_committed)

    def show_about_dialog(self):
        dialog = AboutDialog(self)
        dialog.setWindowTitle("About")
        dialog.exec_()

    def mouse_down_event(self, event):
        self.tool.on_mouse_down(event)

    def mouse_up_event(self, event):
        self.tool.on_mouse_up(event)

    def mouse_move_event(self, event):
        self.tool.on_mouse_move(event)
        self.image_widget.set_image(self.tool.preview)

    def closeEvent(self, event):
        # Create a message box that asks the user if they are sure they want to quit
        reply = QMessageBox.question(
            self,
            "Message",
            "Are you sure you want to quit?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            event.accept()  # User wants to quit
        else:
            event.ignore()  # User does not want to quit


window = MainWindow()
window.show()
exit(app.exec_())
