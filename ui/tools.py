from PyQt5.QtCore import pyqtSignal, QObject
from math import inf
import cv2
from core.commands import LineCommand, FreehandCommand, FloodFillCommand


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

    def __init__(self, img, ctx=None) -> None:
        super().__init__()
        self.clicked = False
        self.img = img
        self.preview = img.copy()
        self.ctx = ctx

    def on_mouse_move(self, event):
        if self.clicked:
            print("Mouse move")
            end = event.pos()
            self.preview = self.img.copy()
            if self.ctx is not None:
                color = self.ctx["color"]
            else:
                color = (0, 0, 0)

            color = list(reversed(color))
            cv2.line(
                self.preview,
                (self.start.x(), self.start.y()),
                (end.x(), end.y()),
                color,
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
                self.img, self.start.x(), self.start.y(), event.x(), event.y(), self.ctx
            )
            command.execute()
            self.commit((command))
        self.clicked = False

    def commit(self, command):
        self.committed.emit(command)


class FreehandTool(Tool):
    def __init__(self, img, ctx=None) -> None:
        super().__init__()
        self.clicked = False
        self.img = img
        self.preview = img.copy()
        self.points = []
        self.left_x = inf
        self.top_y = inf
        self.right_x = -inf
        self.bottom_y = -inf
        self.ctx = ctx

    def on_mouse_move(self, event):
        if self.clicked:
            print("Mouse move")
            end = event.pos()
            # self.preview = self.img.copy()
            if self.ctx is not None:
                color = self.ctx["color"]
            else:
                color = (0, 0, 0)
            cv2.line(
                self.preview,
                (self.start.x(), self.start.y()),
                (end.x(), end.y()),
                list(reversed(color)),
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
            command = FreehandCommand(self.img, self.points, self.ctx)
            command.execute()
            self.commit(command)
        self.points = []
        self.clicked = False

class FloodFillTool(Tool):
    def __init__(self, img, ctx) -> None:
        super().__init__()
        self.img = img
        self.preview = img.copy()
        self.points = []
        self.left_x = inf
        self.top_y = inf
        self.right_x = -inf
        self.bottom_y = -inf
        self.ctx = ctx

    def on_mouse_move(self, event):
        pass

    def on_mouse_down(self, event):
        self.preview = self.img.copy()
        print((event.pos().x(), event.pos().y),)
        
        # print("Mouse down")
        # self.clicked = True
        # self.start = event.pos()
        # self.points = [(self.start.x(), self.start.y())]

    def on_mouse_up(self, event):
        color = self.ctx["color"]
        color = list(reversed(color))
        ret, _, mask, rect = cv2.floodFill(self.preview, None, (event.pos().x(), event.pos().y()), color)
        print(rect)
        command = FloodFillCommand(self.img, (event.pos().x(), event.pos().y()), rect, self.ctx)
        command.execute()
        self.commit(command)