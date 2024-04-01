import os
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = 'C:/Users/Макс/PycharmProjects/pythonProject/.venv/Lib/site-packages/PyQt5/Qt5/plugins'
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QColorDialog, QSpinBox, \
    QUndoStack, QUndoCommand, QFileDialog, QInputDialog, QHBoxLayout, QFrame
from PyQt5.QtGui import QPainter, QColor, QPainterPath, QPen, QImage, QTransform, QPalette
from PyQt5.QtCore import Qt


class AddPathCommand(QUndoCommand):
    def __init__(self, paths, currentPath, penColor, penWidth, brushType, penStyle, drawingArea):
        super().__init__()
        self.paths = paths
        self.currentPath = currentPath
        self.penColor = penColor
        self.penWidth = penWidth
        self.brushType = brushType
        self.penStyle = penStyle
        self.drawingArea = drawingArea

    def undo(self):
        self.paths.pop()
        self.drawingArea.update()

    def redo(self):
        self.paths.append((self.currentPath, self.penColor, self.penWidth, self.brushType, self.penStyle))
        self.drawingArea.update()

class DrawingArea(QWidget):
    def __init__(self, undoStack):
        super().__init__()
        self.setMouseTracking(True)
        self.paths = []
        self.currentPath = None
        self.penColor = QColor('black')
        self.penWidth = 1
        self.penStyle = Qt.SolidLine
        self.undoStack = undoStack
        self.image = QImage(self.size(), QImage.Format_ARGB32)
        self.scale = 1.0
        self.setAcceptDrops(True)
        self.setFixedSize(1176, 642)
        self.brushType = Qt.RoundCap
        self.pen = QPen(self.penColor, self.penWidth, self.penStyle)
        self.pen.setCapStyle(self.brushType)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.rect().contains(event.pos()):
                self.lastPoint = event.pos()
                self.currentPath = QPainterPath()
                self.currentPath.moveTo(event.pos() / self.scale)
                self.pen.setStyle(self.penStyle)

    def mouseReleaseEvent(self, event):
        if self.currentPath is not None:
            self.undoStack.push(
                AddPathCommand(self.paths, self.currentPath, self.penColor, self.penWidth, self.brushType, self.penStyle, self))
            self.currentPath = None

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            if self.rect().contains(event.pos()):
                self.pen.setStyle(self.penStyle)
                self.pen.setWidth(self.penWidth)
                self.pen.setColor(self.penColor)
                self.currentPath.lineTo(event.pos() / self.scale)
                self.update()

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self.scale *= 1.1
        else:
            self.scale /= 1.1
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(self.pen)
        painter.scale(self.scale, self.scale)

        for path, color, width, brushType, penStyle in self.paths:
            pen = QPen(color, width, penStyle)
            pen.setCapStyle(brushType)
            painter.setPen(pen)
            painter.drawPath(path)
        if self.currentPath is not None:
            self.pen.setStyle(self.penStyle)
            painter.setPen(self.pen)
            painter.drawPath(self.currentPath)

    def clearAll(self):
        self.paths.clear()
        self.update()

    def saveImage(self):
        fileName, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "Images (*.png)")
        if fileName:
            tempImage = QImage(self.size(), QImage.Format_ARGB32)
            painter = QPainter(tempImage)
            painter.fillRect(tempImage.rect(),
                             self.palette().color(QPalette.Background))
            for path, color, width, _, penStyle in self.paths:
                transform = QTransform()
                transform.scale(self.scale, self.scale)
                pathTransformed = transform.map(path)
                pen = QPen(color, width, penStyle)
                painter.setPen(pen)
                painter.drawPath(pathTransformed)
            if self.currentPath is not None:
                transform = QTransform()
                transform.scale(self.scale, self.scale)
                pathTransformed = transform.map(self.currentPath)
                painter.setPen(self.pen)
                painter.drawPath(pathTransformed)
            tempImage.save(fileName, "PNG")

    def changeBrushType(self, brushType):
        self.brushType = brushType

    def changePenStyle(self, penStyle):
        self.penStyle = penStyle

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.undoStack = QUndoStack(self)
        self.drawingArea = DrawingArea(self.undoStack)
        self.frame = QFrame(self)
        self.frame.setGeometry(0, 0, 1176, 642)
        self.frame.setStyleSheet("background-color: white; border: 1px solid gray;")
        self.frame.setFixedSize(1176, 642)
        self.drawingArea.setParent(self.frame)
        self.drawingArea.move(0, 0)
        self.colorButton = QPushButton('Color', self)
        self.colorButton.clicked.connect(self.chooseColor)
        self.widthSpinBox = QSpinBox(self)
        self.widthSpinBox.setRange(1, 10)
        self.widthSpinBox.valueChanged.connect(self.chooseWidth)
        self.penStyleButton = QPushButton('Change pen style', self)
        self.penStyleButton.clicked.connect(self.choosePenStyle)
        self.undoButton = QPushButton('Undo', self)
        self.undoButton.clicked.connect(self.undo)
        self.redoButton = QPushButton('Redo', self)
        self.redoButton.clicked.connect(self.redo)
        self.clearButton = QPushButton('Clear all', self)
        self.clearButton.clicked.connect(self.drawingArea.clearAll)
        self.saveButton = QPushButton('Save Image', self)
        self.saveButton.clicked.connect(self.drawingArea.saveImage)
        self.brushTypeButton = QPushButton('Change brush type', self)
        self.brushTypeButton.clicked.connect(self.chooseBrushType)
        self.bgColorButton = QPushButton('Background Color', self)
        self.bgColorButton.clicked.connect(self.chooseBgColor)
        hbox = QHBoxLayout()
        hbox.addWidget(self.colorButton)
        hbox.addWidget(self.widthSpinBox)
        hbox.addWidget(self.penStyleButton)
        hbox.addWidget(self.undoButton)
        hbox.addWidget(self.redoButton)
        hbox.addWidget(self.clearButton)
        hbox.addWidget(self.saveButton)
        hbox.addWidget(self.brushTypeButton)
        hbox.addWidget(self.bgColorButton)
        vbox = QVBoxLayout()
        vbox.addWidget(self.frame)
        vbox.addLayout(hbox)
        self.setLayout(vbox)

    def chooseColor(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.drawingArea.penColor = color

    def chooseWidth(self, width):
        self.drawingArea.penWidth = width

    def undo(self):
        if self.undoStack.canUndo():
            self.undoStack.undo()

    def redo(self):
        if self.undoStack.canRedo():
            self.undoStack.redo()

    def chooseBrushType(self):
        brushTypes = {"Round": Qt.RoundCap, "Square": Qt.SquareCap}
        brushType, ok = QInputDialog.getItem(self, "Select brush type", "Brush type:", list(brushTypes.keys()), 0,
                                             False)
        if ok and brushType:
            self.drawingArea.changeBrushType(brushTypes[brushType])

    def choosePenStyle(self):
        penStyles = {"SolidLine": Qt.SolidLine, "DashLine": Qt.DashLine, "DotLine": Qt.DotLine,
                     "DashDotLine": Qt.DashDotLine, "DashDotDotLine": Qt.DashDotDotLine}
        penStyle, ok = QInputDialog.getItem(self, "Select pen style", "Pen style:", list(penStyles.keys()), 0,
                                            False)
        if ok and penStyle:
            self.drawingArea.changePenStyle(penStyles[penStyle])

    def chooseBgColor(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.drawingArea.setAutoFillBackground(True)
            palette = self.drawingArea.palette()
            palette.setColor(QPalette.Background, color)
            self.drawingArea.setPalette(palette)


app = QApplication([])
window = MainWindow()
window.show()
sys.exit(app.exec())