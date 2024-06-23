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
    # QObject
)
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtCore import pyqtSignal, QObject

import sys

import comm
from ui.about_dialog import AboutDialog
from ui.image_widget import ImageWidget
from core.commands import LineCommand, FreehandCommand, FloodFillCommand


import cv2
import numpy as np

app = QApplication(sys.argv)


class Tool(QObject):
    committed = pyqtSignal(object)

    def commit(self, command):
        self.committed.emit(command)

    def on_mouse_move(self, event):
        pass

    def on_mouse_down(self, event):
        pass

    def on_mouse_up(self, event):
        pass


class LineTool(QObject):

    committed = pyqtSignal(object)

    def __init__(self, img) -> None:
        super().__init__()
        self.clicked = False
        self.img = img
        self.preview = img.copy()

    def on_mouse_move(self, event):
        if self.clicked:
            print("Mouse move")
            end = event.pos()
            self.preview = self.img.copy()
            cv2.line(
                self.preview,
                (self.start.x(), self.start.y()),
                (end.x(), end.y()),
                (0, 255, 0),
                1,
            )

    def on_mouse_down(self, event):
        print("Mouse down")
        self.clicked = True
        self.start = event.pos()

    def on_mouse_up(self, event):
        print("Mouse up")
        if self.clicked:
            command = LineCommand(
                self.img, self.start.x(), self.start.y(), event.x(), event.y()
            )
            command.execute()
            self.commit((command))
        self.clicked = False

    def commit(self, command):
        self.committed.emit(command)


class FreehandTool(Tool):
    def __init__(self, img) -> None:
        super().__init__()
        self.clicked = False
        self.img = img
        self.preview = img.copy()
        self.points = []
        self.left_x = inf
        self.top_y = inf
        self.right_x = -inf
        self.bottom_y = -inf

    def on_mouse_move(self, event):
        if self.clicked:
            print("Mouse move")
            end = event.pos()
            # self.preview = self.img.copy()
            cv2.line(
                self.preview,
                (self.start.x(), self.start.y()),
                (end.x(), end.y()),
                (0, 255, 0),
                1,
            )
            self.points.append((end.x(), end.y()))
            self.start = end
            self.right_x = max(self.right_x, end.x())
            self.left_x = min(self.left_x, end.x())
            self.top_y = min(self.top_y, end.y())
            self.bottom_y = max(self.bottom_y, end.y())

    def on_mouse_down(self, event):
        print("Mouse down")
        self.clicked = True
        self.start = event.pos()
        self.points = [(self.start.x(), self.start.y())]

    def on_mouse_up(self, event):
        print("Mouse up")
        if self.clicked:
            command = FreehandCommand(self.img, self.points)
            command.execute()
            self.commit(command)
        self.clicked = False

class FloodFillTool(Tool):
    def __init__(self, img) -> None:
        super().__init__()
        self.img = img
        self.preview = img.copy()
        self.points = []
        self.left_x = inf
        self.top_y = inf
        self.right_x = -inf
        self.bottom_y = -inf

    def on_mouse_move(self, event):
        pass
        # if self.clicked:
        #     print("Mouse move")
        #     end = event.pos()
        #     # self.preview = self.img.copy()
        #     cv2.line(
        #         self.preview,
        #         (self.start.x(), self.start.y()),
        #         (end.x(), end.y()),
        #         (0, 255, 0),
        #         1,
        #     )
        #     self.points.append((end.x(), end.y()))
        #     self.start = end
        #     self.right_x = max(self.right_x, end.x())
        #     self.left_x = min(self.left_x, end.x())
        #     self.top_y = min(self.top_y, end.y())
        #     self.bottom_y = max(self.bottom_y, end.y())

    def on_mouse_down(self, event):
        self.preview = self.img.copy()
        print((event.pos().x(), event.pos().y),)
        
        # print("Mouse down")
        # self.clicked = True
        # self.start = event.pos()
        # self.points = [(self.start.x(), self.start.y())]

    def on_mouse_up(self, event):
        ret, _, mask, rect = cv2.floodFill(self.preview, None, (event.pos().x(), event.pos().y()), (0, 255, 0))
        print(rect)
        command = FloodFillCommand(self.img, (event.pos().x(), event.pos().y()), rect)
        command.execute()
        self.commit(command)
        # print("Mouse up")
        # if self.clicked:
        #     command = FreehandCommand(self.img, self.points)
        #     command.execute()
        #     self.commit(command)
        # self.clicked = False


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
        self.image_widget.mouse_down.connect(self.mouse_down_event)
        self.image_widget.mouse_up.connect(self.mouse_up_event)
        self.image_widget.mouse_move.connect(self.mouse_move_event)
        self.layout.addWidget(self.image_widget)
        img = np.zeros((512, 512, 3), np.uint8)
        cv2.circle(img, (50, 50), 20, (255, 0, 0), -1)
        self.img = img
        self.image_widget.set_image(img)

        # self.tool = LineTool(img)
        # self.tool = FreehandTool(img)
        self.tool = FloodFillTool(img)
        self.tool.committed.connect(self.on_tool_committed)

    def on_tool_committed(self, command):
        self.undo_stack.append(command)
        self.redo_stack = []
        self.image_widget.set_image(self.img)

    def create_menu(self):
        self.file_menu = self.menubar.addMenu("File")
        self.file_menu.addAction("New")
        self.file_menu.addAction("Open")
        self.file_menu.addAction("Save")
        self.file_menu.addAction("Close")
        self.file_menu.addSeparator()
        self.exit_button = self.file_menu.addAction("Exit")
        self.exit_button.triggered.connect(self.close)

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
        self.tools_menu = self.menubar.addMenu("Tools")
        self.line_tool_action = self.tools_menu.addAction("Line")
        self.freehand_tool_action = self.tools_menu.addAction("Freehand")
        self.flood_fill_tool_action = self.tools_menu.addAction("Flood Fill")


        self.line_tool_action.triggered.connect(self.set_line_tool)
        self.freehand_tool_action.triggered.connect(self.set_freehand_tool)
        self.flood_fill_tool_action.triggered.connect(self.set_flood_fill_tool)

        self.help_menu = self.menubar.addMenu("Help")
        self.about_button = self.help_menu.addAction("About")
        self.about_button.triggered.connect(self.show_about_dialog)

    def undo(self):
        print(self.undo_stack)
        if len(self.undo_stack) > 0:
            command = self.undo_stack.pop()
            self.redo_stack.append(command)
            command.undo()
        self.image_widget.set_image(self.img)

    def set_line_tool(self):
        if self.tool:
            self.tool.committed.disconnect(self.on_tool_committed)
            del self.tool
        self.tool = LineTool(self.img)
        # self.tool = FloodFillTool(self.img)
        self.tool.committed.connect(self.on_tool_committed)

    def set_freehand_tool(self):
        if self.tool:
            self.tool.committed.disconnect(self.on_tool_committed)
            del self.tool
        self.tool = FreehandTool(self.img)
        self.tool.committed.connect(self.on_tool_committed)

    def set_flood_fill_tool(self):
        if self.tool:
            self.tool.committed.disconnect(self.on_tool_committed)
            del self.tool
        self.tool = FloodFillTool(self.img)
        self.tool.committed.connect(self.on_tool_committed)


    def redo(self):
        if len(self.redo_stack) > 0:
            command = self.redo_stack.pop()
            self.undo_stack.append(command)
            command.execute()
        self.image_widget.set_image(self.img)

    def show_about_dialog(self):
        dialog = AboutDialog(self)
        dialog.setWindowTitle("About")
        dialog.exec_()

    def mouse_down_event(self, event):
        print("Mouse down")
        # self.clicked = True
        # self.start = event.pos()
        self.tool.on_mouse_down(event)

    def mouse_up_event(self, event):
        pass
        # print("Mouse up")
        # if self.clicked:
        #     command = LineCommand(self.img, self.start.x(), self.start.y(), event.x(), event.y())
        #     command.execute()
        #     self.undo_stack.append(command)
        #     print(len(self.undo_stack))
        #     self.image_widget.set_image(self.img)
        # self.clicked = False
        self.tool.on_mouse_up(event)

    def mouse_move_event(self, event):
        pass
        # if self.clicked:
        #     print("Mouse move")
        #     end = event.pos()
        #     temp_image = self.img.copy()
        #     cv2.line(temp_image, (self.start.x(), self.start.y()), (end.x(), end.y()), (0, 255, 0), 1)
        #     self.image_widget.set_image(temp_image)
        #     # self.start = end
        self.tool.on_mouse_move(event)
        self.image_widget.set_image(self.tool.preview)


window = MainWindow()
window.show()
exit(app.exec_())
