import cv2
import numpy as np

class LineCommand:
    def __init__(self, buffer, x1, y1, x2, y2, ctx) -> None:
        self.buffer = buffer
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.left = min(x1, x2)
        self.right = max(x1, x2)
        self.top = min(y1, y2)
        self.bottom = max(y1, y2)
        self.ctx = ctx
    def execute(self):
        color = self.ctx["color"]
        color = list(reversed(color))
        self.undo_mask = self.buffer[self.top:self.bottom+1, self.left:self.right+1].copy()
        cv2.line(self.buffer, (self.x1, self.y1), (self.x2, self.y2), color, 1)
    def undo(self):
        self.buffer[self.top:self.bottom+1, self.left:self.right+1] = self.undo_mask.copy()


class FreehandCommand:
    def __init__(self, buffer, points, ctx) -> None:
        self.buffer = buffer
        self.points = points
        self.left = min([p[0] for p in points])
        self.right = max([p[0] for p in points])
        self.top = min([p[1] for p in points])
        self.bottom = max([p[1] for p in points])
        self.ctx = ctx
    def execute(self):
        color = self.ctx["color"]
        color = list(reversed(color))
        self.undo_mask = self.buffer[self.top:self.bottom+1, self.left:self.right+1].copy()
        cv2.polylines(self.buffer, [np.array(self.points)], False, color, 1)
    def undo(self):
        self.buffer[self.top:self.bottom+1, self.left:self.right+1] = self.undo_mask.copy()

class FloodFillCommand:
    def __init__(self, buffer, seed, rect, ctx) -> None:
        self.buffer = buffer
        self.seed = seed
        self.rect = rect
        self.ctx = ctx
        print(self.rect)
        # exit()
    def execute(self):
        color = self.ctx["color"]
        color = list(reversed(color))
        x, y, w, h = self.rect[0], self.rect[1], self.rect[2], self.rect[3]
        self.undo_mask = self.buffer[y:y+h, x:x+w].copy()
        # cv2.floodFill(buffer, None, points, (0, 255, 0))
        cv2.floodFill(self.buffer, None, self.seed, color)
        # cv2.imshow("new buffer", self.buffer)
        # cv2.waitKey(1)t
        print("Executed")
        # cv2.polylines(self.buffer, [np.array(self.points)], False, (0, 255, 0), 1)
    def undo(self):
        # self.buffer[self.top:self.bottom+1, self.left:self.right+1] = self.undo_mask.copy()
        x, y, w, h = self.rect[0], self.rect[1], self.rect[2], self.rect[3]
        self.buffer[y:y+h, x:x+w] = self.undo_mask.copy()