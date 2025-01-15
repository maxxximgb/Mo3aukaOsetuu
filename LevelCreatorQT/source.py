import os
import shutil
import sys
from qasync import QApplication, QEventLoop, asyncSlot
import asyncio
from PIL import Image, ImageDraw
import numpy as np
from PyQt6 import QtCore
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor, QKeyEvent, QImage, QIcon
from PyQt6.QtWidgets import QMainWindow, QPushButton, QStackedWidget, QWidget, QHBoxLayout, QListWidget, \
    QLabel, QListWidgetItem, QVBoxLayout, QMessageBox, QFileDialog, QDialog, QLineEdit, QTextEdit, QStackedLayout, \
    QGridLayout, QProgressBar

currentindexqss = """
        QLabel {
            border-radius: 5px;
            font-family: "Arial";
            font-size: 14px;
            font-weight: bold;
            background-color: blue;
        }
        """
defaultqss = """
        QLabel {
            border-radius: 5px;
            font-family: "Arial";
            font-size: 14px;
            font-weight: bold;
        }
        
        QLabel:hover {
            background-color: gray;
        }
        """

buttonqss = """
        QPushButton {
            background-color: purple;
            border: none;
            color: white; 
            padding: 15px 32px;
            text-align: center;
            font-size: 11px;
            font-weight: bold;
            border-radius: 12px;
            transition: background-color 0.3s ease;
        }
        
        QPushButton:hover {
            background-color: blue;
        }
        
        QPushButton:pressed {
            background-color: black;
        }
        """
loadbtnqss = """
        QPushButton {
            background-color: #e0e0e0;
            color: black;
            border: 1px solid #808080;
            border-radius: 5px;
            padding: 10px 20px;
            font-weight: bold;
        }
        
        QPushButton:hover {
            background-color: #c0c0c0;
        }
        
        QPushButton:pressed {
            background-color: #a0a0a0;
        }
        """
imgqss = """
            QLabel {
                border-radius: 10px;
                border: 2px solid black;
                padding: 5px;
            }
            QLabel:hover {
                border-radius: 10px;
                background-color: gray;
            }
        """
map = None
AvInd = [1]
levels = []


def getabspath(path):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, path)


class CentralWidget(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.widgets = []

    def initialize(self):
        self.widgets = [
            Beginning(),
            LoadingMap(),
            CreatingLevels(),
            Finishing()
        ]
        for widget in self.widgets:
            self.addWidget(widget)
        self.setCurrentIndex(0)


class StackedWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.index = -1
        self.mlout = QVBoxLayout()
        self.lout = QHBoxLayout()
        self.indexes = QListWidget()
        self.indexes.setSpacing(15)
        self.indexes.setMaximumSize(200, 500)
        self.indexes.setMinimumSize(190, 170)
        self.nextbtn = QPushButton(self)
        self.nextbtn.setStyleSheet(buttonqss)
        self.nextbtn.clicked.connect(self.nextwidget)
        self.nextbtn.setText("Далее")
        self.labels = [QLabel(" Начало"),
                       QLabel(" Загрузка карты"),
                       QLabel(" Создание уровней"),
                       QLabel(" Сохранение")]
        [self.addItemToList(l) for l in self.labels]
        self.indexes.itemClicked.connect(self.OIC)
        self.lout.addWidget(self.indexes, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.mlout.addLayout(self.lout)
        self.mlout.addWidget(self.nextbtn, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
        self.setLayout(self.mlout)

    def OIC(self, item):
        global AvInd
        index = self.indexes.row(item)
        if index < self.index:
            self.parent().setCurrentIndex(index)
        elif index in AvInd:
            self.parent().setCurrentIndex(index)
        else:
            self.showMbox()

    def showMbox(self):
        box = QMessageBox(self, icon=QMessageBox.Icon.Warning, text="Заполните значения в предыдущих окнах!")
        box.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.CustomizeWindowHint)
        box.exec()

    def addItemToList(self, a):
        a.setStyleSheet(defaultqss)
        item = QListWidgetItem()
        self.indexes.addItem(item)
        self.indexes.setItemWidget(item, a)

    def nextwidget(self):
        if self.index + 1 not in AvInd:
            box = QMessageBox(self, icon=QMessageBox.Icon.Warning, text="Не все поля заполнены!")
            box.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.CustomizeWindowHint)
            box.exec()
            return
        self.parent().setCurrentIndex(self.index + 1)
        if self.index + 1 not in AvInd: AvInd.append(self.index + 1)


class Beginning(StackedWidget):
    def __init__(self):
        super().__init__()
        self.index = 0
        self.indexes.itemWidget(self.indexes.item(self.index)).setStyleSheet(currentindexqss)
        self.label = QLabel(
            "Здравствуйте! Cейчас мы поможем Вам создать уровни для игры 'Мозаика Осетии'.\n"
            "Для того, чтобы приступить, нажмите на кнопку Далее, или выберите слева второй пункт.")
        self.label.setStyleSheet("""
        QLabel {
            font-size: 25px;
        }
        """)
        self.lout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignTop)


class LoadingMap(StackedWidget):
    def __init__(self):
        super().__init__()
        self.index = 1
        self.pixmap = QPixmap()
        self.imagelabel = QLabel()
        self.indexes.itemWidget(self.indexes.item(self.index)).setStyleSheet(currentindexqss)
        self.imagelout = QVBoxLayout()
        self.selectMapBtn = QPushButton(text="Загрузить")
        self.selectMapBtn.setStyleSheet(loadbtnqss)
        self.selectMapBtn.clicked.connect(self.selectImage)
        self.imagelout.addWidget(self.imagelabel, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter)
        self.imagelout.addWidget(self.selectMapBtn, alignment=Qt.AlignmentFlag.AlignCenter)
        self.imagelout.addWidget(QLabel(text="Загрузите карту для уровня.\n"
                                             "Нажмите на кнопку Загрузить и укажите путь к вашей карте."),
                                 alignment=Qt.AlignmentFlag.AlignCenter)
        self.imagelout.itemAt(2).widget().setStyleSheet("""
        QLabel {
            font-size: 15px;
        }
        """)
        self.lout.addLayout(self.imagelout)
        self.loadImage(getabspath("Preview.jpg"))

    def loadImage(self, path):
        self.pixmap.load(getabspath(path))
        self.imagelabel.setPixmap(self.pixmap)
        global levels, map
        buffer = QtCore.QBuffer()
        buffer.open(QtCore.QIODevice.OpenModeFlag.ReadWrite)
        self.pixmap.save(buffer, "PNG")
        map = buffer.data()
        buffer.close()
        levels.clear()

    def selectImage(self):
        path, _ = QFileDialog.getOpenFileName(self, "Выберите изображение", "",
                                              "Images (*.bmp *.gif *.jpg *.jpeg *.png *.pbm *.pgm *.ppm *.xbm *.xpm)")
        if path:
            self.loadImage(path)
            global AvInd
            if self.index + 1 not in AvInd: AvInd.append(self.index + 1)
            self.parent().widgets[2].setImage(self.pixmap)


class CreatingLevels(StackedWidget):
    def __init__(self):
        super().__init__()
        self.index = 2
        self.indexes.itemWidget(self.indexes.item(self.index)).setStyleSheet(currentindexqss)
        self.imagelout = QVBoxLayout()
        self.setMouseTracking(True)
        self.imagelabel = MapLabel()
        self.imagetext = QLabel(text="Выберите точки на карте, где будут находиться города.\n"
                                     "Для этого щелкните мышкой по нужным вам точкам на карте.\n"
                                     "Первая отмеченая точка будет не игровой и будет являться точкой старта пользователя.\n"
                                     "Типа въезд в город.\n"
                                     "Для удаления точки наведите на нее курсор и нажмите delete.\n"
                                     "Нажмите еще раз на созданную точку чтобы открыть меню её редактирования.")
        self.imagetext.setStyleSheet("""
        QLabel {
            font-size: 15px;
        }
        """)
        self.imagelout.addWidget(self.imagelabel, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter)
        self.imagelout.addWidget(self.imagetext, alignment=Qt.AlignmentFlag.AlignCenter)
        self.lout.addLayout(self.imagelout)

    def mousePressEvent(self, a0):
        if self.imagelabel.geometry().contains(a0.position().toPoint()):
            local_pos = self.imagelabel.mapFromGlobal(a0.globalPosition().toPoint())
            global levels
            for level in levels:
                posi = level[0]
                if abs(posi.x() - local_pos.x()) < 10 and abs(posi.y() - local_pos.y()) < 10:
                    print(levels.index(level))
                    if levels.index(level) == 0:
                        return
                    data = LevelRedactor(level[1]).execute()
                    if data is not None:
                        level[1] = data
                    self.imagelabel.update()
                    return

            levels.append([local_pos, LevelData()])
            if len(levels) > 1 and 3 not in AvInd:
                AvInd.append(3)
            elif len(levels) < 2 and 3 in AvInd:
                AvInd.remove(3)
            self.imagelabel.update()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete:
            global levels
            mouse_pos = self.imagelabel.mapFromGlobal(self.cursor().pos())
            for posi in levels:
                pos = posi[0]
                if abs(pos.x() - mouse_pos.x()) < 10 and abs(pos.y() - mouse_pos.y()) < 10:
                    levels.remove(posi)
                    self.imagelabel.update()
                    if len(levels[1:]) == 0 and 3 in AvInd: AvInd.remove(3)
                    return

    def setImage(self, pixmap):
        self.imagelabel.setPixmap(pixmap)
        self.imagelabel.ispixmap = True


class MapLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.ispixmap = False
        self.setMouseTracking(True)

    def paintEvent(self, event):
        super().paintEvent(event)
        global levels
        if not self.ispixmap: return
        if not levels: return
        redPen = QColor(255, 0, 0)
        bluePen = QColor(0, 0, 255)
        greenPen = QColor(0, 255, 0)
        yellowPen = QColor(255, 255, 0)
        painter = QPainter(self)
        painter.setPen(bluePen)
        painter.setBrush(bluePen)
        painter.drawEllipse(levels[0][0], 10, 10)

        for level in levels[1::]:
            pos = level[0]
            if level[1].isFilled == 1:
                painter.setPen(greenPen)
                painter.setBrush(greenPen)
            elif level[1].isFilled == 2:
                painter.setPen(yellowPen)
                painter.setBrush(yellowPen)
            else:
                painter.setPen(redPen)
                painter.setBrush(redPen)
            painter.drawEllipse(pos, 10, 10)

    def mouseMoveEvent(self, event):
        global levels
        mouse_pos = self.mapFromGlobal(self.cursor().pos())
        for pos in levels:
            pos = pos[0]
            if abs(pos.x() - mouse_pos.x()) < 10 and abs(pos.y() - mouse_pos.y()) < 10:
                self.setCursor(Qt.CursorShape.PointingHandCursor)
                return

        self.setCursor(Qt.CursorShape.ArrowCursor)


class LevelData:
    def __init__(self):
        self.isFilled = 0
        self.images = []
        self.name = ''
        self.desc = ''
        self.memorials = []


class Memorial:
    def __init__(self, preview):
        self.isFilled = False
        self.preview = preview
        self.images = []
        self.name = ''
        self.desc = ''
        self.puzzleparts = []
        self.puzzle = None


class LevelEditorWidget(QWidget):
    def __init__(self, LevelData):
        super().__init__()
        self.levelData = LevelData
        self.nextbtn = QPushButton(text="Далее")
        self.nextbtn.setStyleSheet(buttonqss)
        self.nextbtn.setFixedSize(100, 50)
        self.nextbtn.clicked.connect(self.saveData)
        self.images = [[DClickImgLabel(), QPixmap(), False] for _ in range(4)]
        self.lout = QHBoxLayout()
        self.objlout = QVBoxLayout()
        self.mimageslout = QVBoxLayout()
        self.imagelout1 = QHBoxLayout()
        self.imagelout2 = QHBoxLayout()
        self.nameinput = QLineEdit()
        self.descinput = QTextEdit()
        self.nameinput.setPlaceholderText("Введите название обьекта")
        self.descinput.setPlaceholderText("Введите описание обьекта")
        self.objlout.addWidget(self.nameinput)
        self.objlout.addWidget(self.descinput)
        self.objlout.addWidget(self.nextbtn, alignment=Qt.AlignmentFlag.AlignRight)
        for i in range(2):
            self.imagelout1.addWidget(self.images[i][0], alignment=Qt.AlignmentFlag.AlignLeft)
            self.imagelout2.addWidget(self.images[i + 2][0], alignment=Qt.AlignmentFlag.AlignLeft)
            self.images[i][0].hide()
            self.images[i + 2][0].hide()

        self.images[0][0].show()
        self.mimageslout.addLayout(self.imagelout1)
        self.mimageslout.addLayout(self.imagelout2)
        self.textlabel = QLabel(text="Загрузите фотографии обьекта 16:9, нажав на выделенное изображение сверху.\n"
                                     "Максимум изображений: 4")
        self.textlabel.setStyleSheet("""
            QLabel {
                font-size: 15px;
            }
        """)
        self.textlabel.setMinimumWidth(500)
        self.textlabel.setWordWrap(True)

        self.mimageslout.addWidget(self.textlabel, alignment=Qt.AlignmentFlag.AlignLeft)
        self.lout.addLayout(self.mimageslout)
        self.lout.addLayout(self.objlout)
        self.setLayout(self.lout)
        self.loadData()

    def addImage(self, image, type="file"):
        for img in self.images:
            if not img[2]:
                if type == "file":
                    img[1].load(image)
                elif type == "buffer":
                    img[1].loadFromData(image)
                img[1] = img[1].scaled(300, 150, Qt.AspectRatioMode.KeepAspectRatio,
                                       Qt.TransformationMode.SmoothTransformation)
                img[0].setPixmap(img[1])
                img[0].setFixedSize(img[1].size())
                img[2] = True
                img[0].setAlignment(Qt.AlignmentFlag.AlignLeft)
                img[0].show()
                if self.images.index(img) == 3:
                    img[0].setStyleSheet("")
                else:
                    img[0].clicked.connect(self.selectImage)
                break
            else:
                if img[0].styleSheet():
                    img[0].clicked.disconnect()
                    img[0].setStyleSheet("")

    def selectImage(self):
        path, _ = QFileDialog.getOpenFileName(self, "Выберите изображение", "",
                                              "Images (*.bmp *.gif *.jpg *.jpeg *.png *.pbm *.pgm *.ppm *.xbm *.xpm)")
        if path:
            self.addImage(path)

    def loadData(self):
        if not self.levelData.isFilled:
            self.addImage(getabspath("add.png"))
            self.images[0][2] = False
        else:
            for img in self.levelData.images:
                self.addImage(img, type="buffer")
            self.nameinput.setText(self.levelData.name)
            self.descinput.setText(self.levelData.desc)

    def saveData(self):
        isPixmap = any([pixmap[2] for pixmap in self.images])
        isDesc = self.descinput.toPlainText()
        isName = self.nameinput.text()

        if not isPixmap:
            self.images[0][0].setStyleSheet(imgqss.replace("black", "red"))
        if not isName:
            self.nameinput.setStyleSheet("""
            QLineEdit {
                border: 2px solid red;
                border-radius: 4px;
            }
            """)
            self.nameinput.textChanged.connect(lambda: self.nameinput.setStyleSheet(""))
        if not isDesc:
            self.descinput.setStyleSheet("""
            QTextEdit {
                border: 2px solid red;
                padding: 2px;
                border-radius: 4px;
            }
            """)
            self.descinput.textChanged.connect(lambda: self.descinput.setStyleSheet(""))

        if all([isPixmap, isName, isDesc]):
            self.levelData.images.clear()
            for image in self.images:
                if image[2]:
                    pixmap = image[1]
                    buffer = QtCore.QBuffer()
                    buffer.open(QtCore.QIODevice.OpenModeFlag.ReadWrite)
                    pixmap.save(buffer, "PNG")
                    self.levelData.images.append(buffer.data())
                    buffer.close()

            self.levelData.name = isName
            self.levelData.desc = isDesc
            if self.levelData.isFilled != 1:
                self.levelData.isFilled = 2
            self.parent().stackedLayout.setCurrentIndex(1)


class MemorialSelectorWidget(QWidget):
    def __init__(self, LevelData):
        super().__init__()
        self.lout = QVBoxLayout()
        self.grid_layout = QGridLayout()
        self.backBtn = QPushButton(text='Назад')
        self.saveBtn = QPushButton(text="Сохранить")
        self.btnLayout = QHBoxLayout()
        self.saveBtn.clicked.connect(self.saveData)
        self.saveBtn.setStyleSheet(buttonqss)
        self.backBtn.setStyleSheet(buttonqss)
        self.backBtn.clicked.connect(lambda: self.parent().stackedLayout.setCurrentIndex(0))
        self.btnLayout.addWidget(self.backBtn, alignment=Qt.AlignmentFlag.AlignRight)
        self.btnLayout.addWidget(self.saveBtn, alignment=Qt.AlignmentFlag.AlignRight)
        self.btnLayout.setSpacing(3)
        self.levelData = LevelData
        self.memorials = []
        self.label = QLabel('Добавьте мемориалы выбранного города')
        self.label.setStyleSheet(defaultqss)
        self.lout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter)
        self.lout.addLayout(self.grid_layout)
        self.lout.addLayout(self.btnLayout)
        self.btnLayout.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.setLayout(self.lout)
        self.loadData()

    def addImage(self, image, type="file"):
        pixmap = QPixmap()
        label = DClickImgLabel()
        pixmap.loadFromData(image.preview) if type == "class" else pixmap.load(image)
        pixmap = pixmap.scaled(400, 300, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        if not self.memorials:
            label.setPixmap(pixmap)
            self.memorials.append([label, Memorial(image) if type == 'file' else image, False])
        else:
            for i, (label, memorial, is_temp) in enumerate(self.memorials):
                if is_temp:
                    label.setPixmap(pixmap)
                    if type == 'file':
                        buffer = QtCore.QBuffer()
                        buffer.open(QtCore.QIODevice.OpenModeFlag.ReadWrite)
                        pixmap.save(buffer, "PNG")
                        image = buffer.data()
                        buffer.close()

                    self.memorials[i][1:] = Memorial(image) if type == 'file' else image, False
                    self.memorials[i][0].clicked.disconnect()
                    self.memorials[i][0].clicked.connect(lambda: MemorialEditorWidget(self.memorials[i][1]).exec())

        self.addTempImage()

    def addTempImage(self):
        img_label = DClickImgLabel()
        pixmap = QPixmap(getabspath("addmem.png"))
        pixmap = pixmap.scaled(400, 300, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        img_label.setPixmap(pixmap)
        img_label.show()
        self.memorials.append([img_label, pixmap, True])
        row = (len(self.memorials) - 1) // 2
        col = (len(self.memorials) - 1) % 2
        self.grid_layout.addWidget(img_label, row, col,
                                   alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        img_label.clicked.connect(self.selectImage)

    def loadData(self):
        self.addTempImage()
        if self.levelData.memorials:
            for memorial in self.levelData.memorials:
                self.addImage(memorial, type="class")

    def selectImage(self):
        path, _ = QFileDialog.getOpenFileName(self, "Выберите изображение", "",
                                              "Images (*.bmp *.gif *.jpg *.jpeg *.png *.pbm *.pgm *.ppm *.xbm *.xpm)")
        if path:
            self.addImage(path)

    def saveData(self):
        fl = False
        if len(self.memorials) == 1:
            self.memorials[0][0].setStyleSheet(imgqss.replace("black", "red"))
            return
        for memorial in self.memorials:
            if memorial[2]: continue
            if not memorial[1].isFilled:
                fl = True
                memorial[0].setStyleSheet(imgqss.replace("black", "red"))
        if fl: return
        self.levelData.memorials = [m[1] for m in self.memorials if m[2] != True]
        self.levelData.isFilled = 1
        self.parent().close()


class MemorialEditorWidget(QDialog):
    def __init__(self, memorial):
        super().__init__()
        self.setWindowTitle("Редактор данных мемориала")
        self.memorial = memorial
        self.savebtn = QPushButton(text="Сохранить")
        self.savebtn.setStyleSheet(buttonqss)
        self.savebtn.setFixedSize(150, 50)
        self.savebtn.clicked.connect(self.saveData)
        self.images = [[DClickImgLabel(), QPixmap(), False] for _ in range(4)]
        self.lout = QHBoxLayout()
        self.objlout = QVBoxLayout()
        self.mimageslout = QVBoxLayout()
        self.imagelout1 = QHBoxLayout()
        self.imagelout2 = QHBoxLayout()
        self.nameinput = QLineEdit()
        self.descinput = QTextEdit()
        self.puzzle = QPixmap()
        self.puzzlepartl = DClickImgLabel()
        self.puzzlepartl.setPixmap(self.puzzle)
        self.puzzlepartl.clicked.connect(lambda: self.selectImage(type='puzzle'))
        self.nameinput.setPlaceholderText("Введите название мемориала")
        self.descinput.setPlaceholderText("Введите описание мемориала")
        self.objlout.addWidget(self.nameinput)
        self.objlout.addWidget(self.descinput)
        self.objlout.addWidget(self.savebtn, alignment=Qt.AlignmentFlag.AlignRight)
        for i in range(2):
            self.imagelout1.addWidget(self.images[i][0], alignment=Qt.AlignmentFlag.AlignLeft)
            self.imagelout2.addWidget(self.images[i + 2][0], alignment=Qt.AlignmentFlag.AlignLeft)
            self.images[i][0].hide()
            self.images[i + 2][0].hide()

        self.images[0][0].show()
        self.mimageslout.addLayout(self.imagelout1)
        self.mimageslout.addLayout(self.imagelout2)
        self.textlabel = QLabel(text="Загрузите фотографии мемориала 16:9, нажав на выделенное изображение сверху.\n"
                                     "Максимум изображений: 4")
        self.textlabel.setStyleSheet("""
            QLabel {
                font-size: 15px;
            }
        """)
        self.textlabel.setMinimumWidth(500)
        self.textlabel.setWordWrap(True)
        self.puzzletextl = QLabel('Загрузите изображение, которое будет раздроблено на пазл мемориала')
        self.puzzletextl.setStyleSheet("""
            QLabel {
                font-size: 15px;
            }
        """)
        self.mimageslout.addWidget(self.textlabel, alignment=Qt.AlignmentFlag.AlignLeft)
        self.mimageslout.addWidget(self.puzzletextl)
        self.mimageslout.addWidget(self.puzzlepartl)
        self.lout.addLayout(self.mimageslout)
        self.lout.addLayout(self.objlout)
        self.setLayout(self.lout)
        self.loadData()

    def addImage(self, image, type="file"):
        for img in self.images:
            if not img[2]:
                if type == "file":
                    img[1].load(image)
                elif type == "buffer":
                    img[1].loadFromData(image)
                img[1] = img[1].scaled(300, 150, Qt.AspectRatioMode.KeepAspectRatio,
                                       Qt.TransformationMode.SmoothTransformation)
                img[0].setPixmap(img[1])
                img[0].setFixedSize(img[1].size())
                img[2] = True
                img[0].setAlignment(Qt.AlignmentFlag.AlignLeft)
                img[0].show()
                if self.images.index(img) == 3:
                    img[0].setStyleSheet("")
                else:
                    img[0].clicked.connect(self.selectImage)
                break
            else:
                if img[0].styleSheet():
                    img[0].clicked.disconnect()
                    img[0].setStyleSheet("")

    def selectImage(self, type='default'):
        path, _ = QFileDialog.getOpenFileName(self, "Выберите изображение", "",
                                              "Images (*.bmp *.gif *.jpg *.jpeg *.png *.pbm *.pgm *.ppm *.xbm *.xpm)")
        if not path: return
        if type == 'puzzle':
            self.loadpuzzle(path)
            return
        if path:
            self.addImage(path)

    def loadpuzzle(self, file, type='file'):
        if type == 'file':
            self.puzzle.load(file)
            self.puzzle = self.puzzle.scaled(1500, 1500, Qt.AspectRatioMode.KeepAspectRatio,
                                             Qt.TransformationMode.SmoothTransformation)
            buffer = QtCore.QBuffer()
            buffer.open(QtCore.QIODevice.OpenModeFlag.ReadWrite)
            self.puzzle.save(buffer, "PNG")
            self.memorial.puzzle = buffer.data()
            buffer.close()

        else:
            self.puzzle.loadFromData(file)

        self.puzzle = self.puzzle.scaled(600, 600, Qt.AspectRatioMode.KeepAspectRatio,
                                         Qt.TransformationMode.SmoothTransformation)
        self.puzzlepartl.setPixmap(self.puzzle)
        self.puzzlepartl.setFixedSize(self.puzzle.size())

    def loadData(self):
        if not self.memorial.isFilled:
            self.addImage(getabspath("add.png"))
            self.puzzle.load(getabspath("addmem.png"))
            self.puzzle = self.puzzle.scaled(400, 400, Qt.AspectRatioMode.KeepAspectRatio,
                                             Qt.TransformationMode.SmoothTransformation)
            self.puzzlepartl.setPixmap(self.puzzle)
            self.puzzlepartl.setFixedSize(400, 400)
            self.images[0][2] = False
        else:
            for img in self.memorial.images:
                self.addImage(img, type="buffer")
            self.loadpuzzle(self.memorial.puzzle, type='image')
            self.nameinput.setText(self.memorial.name)
            self.descinput.setText(self.memorial.desc)

    def saveData(self):
        isPixmap = any([pixmap[2] for pixmap in self.images])
        isDesc = self.descinput.toPlainText()
        isName = self.nameinput.text()
        isPuzzle = self.memorial.puzzle

        if not isPixmap:
            self.images[0][0].setStyleSheet(imgqss.replace("black", "red"))
        if not isName:
            self.nameinput.setStyleSheet("""
            QLineEdit {
                border: 2px solid red;
                border-radius: 4px;
            }
            """)
            self.nameinput.textChanged.connect(lambda: self.nameinput.setStyleSheet(""))
        if not isDesc:
            self.descinput.setStyleSheet("""
            QTextEdit {
                border: 2px solid red;
                padding: 2px;
                border-radius: 4px;
            }
            """)
            self.descinput.textChanged.connect(lambda: self.descinput.setStyleSheet(""))
        if not isPuzzle:
            self.puzzlepartl.setStyleSheet(imgqss.replace("black", "red"))

        if all([isPixmap, isName, isDesc, isPuzzle]):
            self.memorial.images.clear()
            for image in self.images:
                if image[2]:
                    pixmap = image[1]
                    buffer = QtCore.QBuffer()
                    buffer.open(QtCore.QIODevice.OpenModeFlag.ReadWrite)
                    pixmap.save(buffer, "PNG")
                    self.memorial.images.append(buffer.data())
                    buffer.close()

            self.memorial.puzzleparts = self.bytesToPuzzle(self.memorial.puzzle)
            self.memorial.name = isName
            self.memorial.desc = isDesc
            self.memorial.isFilled = True
            self.close()

    def bytesToPuzzle(self, bytes):
        image = QImage()
        image.loadFromData(bytes)
        pixmap = QPixmap.fromImage(image)
        width = pixmap.width()
        height = pixmap.height()

        min_grid_size = 15
        max_grid_size = 25

        aspect_ratio = width / height
        if aspect_ratio > 1:
            cols = min(max_grid_size, max(min_grid_size, int((width / height) * min_grid_size)))
            rows = min(max_grid_size, max(min_grid_size, int(min_grid_size / (width / height))))
        else:
            rows = min(max_grid_size, max(min_grid_size, int((height / width) * min_grid_size)))
            cols = min(max_grid_size, max(min_grid_size, int(min_grid_size / (height / width))))

        rows = min(rows, height)
        cols = min(cols, width)
        piece_width = width // cols
        piece_height = height // rows
        puzzle_matrix = np.empty((rows, cols), dtype=object)

        for i in range(rows):
            for j in range(cols):
                piece = pixmap.copy(j * piece_width, i * piece_height, piece_width, piece_height)
                qimage = piece.toImage()
                pil_image = Image.fromqimage(qimage)
                puzzle_matrix[i, j] = pil_image

        return puzzle_matrix


class LevelRedactor(QDialog):
    def __init__(self, LevelData):
        super().__init__()
        self.levelData = LevelData
        self.setWindowTitle("Редактирование данных уровня")
        self.resize(900, 400)

        self.stackedLayout = QStackedLayout()
        self.setLayout(self.stackedLayout)

        self.levelEditorWidget = LevelEditorWidget(self.levelData)
        self.memorialSelectorWidget = MemorialSelectorWidget(self.levelData)
        self.stackedLayout.addWidget(self.levelEditorWidget)
        self.stackedLayout.addWidget(self.memorialSelectorWidget)

    def execute(self):
        self.exec()
        return self.levelData if self.levelData.isFilled > 0 else None


class Finishing(StackedWidget):
    def __init__(self):
        super().__init__()
        self.index = 3
        self.indexes.itemWidget(self.indexes.item(self.index)).setStyleSheet(currentindexqss)
        self.nextbtn.hide()
        self.vlayout = QVBoxLayout()
        self.lout.addLayout(self.vlayout)
        self.label = QLabel("Укажите путь для сохранения уровня")
        self.label.setStyleSheet("""
        QLabel {
            font-size: 25px;
        }
        """)
        self.vlayout.addWidget(self.label)
        self.sw = None
        self.path_layout = QHBoxLayout()
        self.path_line_edit = QLineEdit(self)
        self.path_line_edit.setPlaceholderText("Выберите путь для сохранения")
        self.path_line_edit.setReadOnly(True)
        self.path_line_edit.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #ccc;
                border-radius: 5px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #6a9eda;
            }
        """)
        self.path_layout.addWidget(self.path_line_edit)
        self.select_path_button = QPushButton(self)
        self.select_path_button.setIcon(QIcon.fromTheme("folder"))
        self.select_path_button.setStyleSheet("""
            QPushButton {
                background-color: #6a9eda;
                border: none;
                border-radius: 5px;
                padding: 8px;
                min-width: 40px;
            }
            QPushButton:hover {
                background-color: #5a8ec9;
            }
            QPushButton:pressed {
                background-color: #4a7db9;
            }
        """)
        self.select_path_button.clicked.connect(self.show_file_dialog)
        self.path_layout.addWidget(self.select_path_button)
        self.vlayout.addLayout(self.path_layout)
        self.vlayout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.saveBtn = QPushButton(text='Сохранить')
        self.saveBtn.clicked.connect(self.check)
        self.saveBtn.setStyleSheet(buttonqss)
        self.vlayout.addWidget(self.saveBtn, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)

    def show_file_dialog(self):
        path, _ = QFileDialog.getSaveFileName(self, "Выберите путь для сохранения", "", "Файлы уровней (*.level)")

        if path:
            self.path_line_edit.setText(path)

    def check(self):
        if not self.path_line_edit.text():
            self.path_line_edit.setStyleSheet("""
                QLineEdit {
                    padding: 8px;
                    border: 2px solid red;
                    border-radius: 5px;
                    font-size: 14px;
                }
                QLineEdit:focus {
                    border-color: red;
                }
            """)
            self.path_line_edit.textChanged.connect(lambda: self.path_line_edit.setStyleSheet("""
                QLineEdit {
                    padding: 8px;
                    border: 2px solid #ccc;
                    border-radius: 5px;
                    font-size: 14px;
                }
                QLineEdit:focus {
                    border-color: #6a9eda;
                }
            """))
            return

        global window
        window.hide()
        self.sw = SaveWidget(self.path_line_edit.text())
        r = self.sw.checkAndSave()
        if not r: window.show()


class SaveWidget(QWidget):
    def __init__(self, directory):
        super().__init__()
        self.dir = directory
        self.setWindowTitle('Выполняется сохранение')
        self.lout = QVBoxLayout()
        self.donelout = QVBoxLayout()
        self.progressbar = QProgressBar()
        self.progresslabel = QLabel()
        self.lout.addWidget(self.progresslabel, alignment=Qt.AlignmentFlag.AlignCenter)
        self.lout.addWidget(self.progressbar, alignment=Qt.AlignmentFlag.AlignCenter)
        self.donelabel = QLabel(
            text='Поздравляем, вы успешно создали уровень. Он находится в указаной вами папке. Спасибо за использование программы! Для повторного использования перезапустите программу. Автоматический выход через 10 секунд.')
        self.donelout.addWidget(self.donelabel)
        self.exitbtn = QPushButton(text='Выход')
        self.donelout.addWidget(self.exitbtn)
        self.exitbtn.clicked.connect(os.abort)
        self.setStyleSheet("""
            QWidget {
                background-color: #2E3440;
                color: #D8DEE9;
                font-size: 16px;
            }
            QProgressBar {
                background-color: #4C566A;
                color: #D8DEE9;
                border: 2px solid #5E81AC;
                border-radius: 5px;
                text-align: center;
                height: 30px;
            }
            QProgressBar::chunk {
                background-color: #81A1C1;
                border-radius: 3px;
            }
            QLabel {
                color: #ECEFF4;
                font-size: 18px;
            }
            QPushButton {
                background-color: #4C566A;
                color: #ECEFF4;
                border: 2px solid #5E81AC;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5E81AC;
                border: 2px solid #81A1C1;
            }
            QPushButton:pressed {
                background-color: #81A1C1;
                border: 2px solid #4C566A;
            }
        """)
        self.setLayout(self.lout)

    def checkAndSave(self):
        global levels
        if not levels:
            QMessageBox(QMessageBox.Icon.Critical, 'Нечего сохранять', 'Вам нечего сохранять! Уровни не созданы!',
                        QMessageBox.StandardButton.Ok).exec()
            return False
        nfl = 0
        for level in levels[1:]:
            print(level)
            if level[1].isFilled != 1:
                nfl += 1
        if nfl > 0:
            QMessageBox(QMessageBox.Icon.Warning, 'Некоторые уровни не заполнены!',
                        'Некоторые уровни не заполнены или заполнены не до конца!\nПроверьте карту в третьем пункте на наличие желтых или красных кружков.\nЗаполните их или удалите. ',
                        QMessageBox.StandardButton.Ok).exec()
            return False
        asyncio.ensure_future(self.save())
        return True

    @asyncSlot()
    async def save(self):
        self.show()
        self.resize(400, 200)

        self.progresslabel.setText('Создание временной папки')
        if not os.path.exists('temp'):
            os.mkdir('temp')
        else:
            shutil.rmtree('temp'), os.mkdir('temp')
        self.progressbar.setValue(self.progressbar.value() + 15)
        self.progresslabel.setText(f'Сохранение карты')
        global map
        file = QtCore.QFile(f'temp/map.png')
        file.open(QtCore.QIODevice.OpenModeFlag.ReadWrite)
        file.write(map)
        file.close()
        await asyncio.sleep(0.2)
        pr = 50 / len(levels)
        self.progresslabel.setText('Сохранение информации о точке входа')
        with open('temp/ep.pos', 'w', encoding='UTF-8') as f:
            f.write(f'{levels[0][0].x()} {levels[0][0].y()}')

        self.progressbar.setValue(self.progressbar.value() + 2)
        await asyncio.sleep(0.2)
        for i, level in enumerate(levels[1:]):
            self.progresslabel.setText(f'Сохранение информации о уровне {level[1].name}')
            os.mkdir(f'temp/{i}')
            with open(f'temp/{i}/info.txt', 'w', encoding='UTF-8') as f:
                f.writelines('\n'.join([level[1].name.replace('\n', ' '), level[1].desc.replace('\n', ' '), f'{level[0].x()} {level[0].y()}']))
            await asyncio.sleep(1)
            self.progresslabel.setText(f'Сохранение изображений уровня {level[1].name}')
            os.mkdir(f'temp/{i}/images')
            for j, image in enumerate(level[1].images):
                file = QtCore.QFile(f'temp/{i}/images/{j}.png')
                file.open(QtCore.QIODevice.OpenModeFlag.ReadWrite)
                file.write(image)
                file.close()
            await asyncio.sleep(0.2)
            os.mkdir(f'temp/{i}/memorials')
            for n, memorial in enumerate(level[1].memorials):
                self.progresslabel.setText(f'Сохранение информации о мемориале {memorial.name} уровня {level[1].name}')
                os.mkdir(f'temp/{i}/memorials/{n}')
                with open(f'temp/{i}/memorials/{n}/info.txt', 'w', encoding='UTF-8') as f:
                    f.writelines('\n'.join([memorial.name.replace('\n', ' '), memorial.desc.replace('\n', ' ')]))
                await asyncio.sleep(0.2)
                self.progresslabel.setText(
                    f'Сохранение изображений предпросмотра мемориала и пазла {memorial.name} уровня {level[1].name}')
                os.mkdir(f'temp/{i}/memorials/{n}/images')
                file = QtCore.QFile(f'temp/{i}/memorials/{n}/images/preview.png')
                file.open(QtCore.QIODevice.OpenModeFlag.ReadWrite)
                file.write(memorial.preview)
                file.close()
                file = QtCore.QFile(f'temp/{i}/memorials/{n}/images/puzzle.png')
                file.open(QtCore.QIODevice.OpenModeFlag.ReadWrite)
                file.write(memorial.preview)
                file.close()
                await asyncio.sleep(0.2)
                self.progresslabel.setText(f'Сохранение изображений мемориала {memorial.name} уровня {level[1].name}')

                for z, image in enumerate(memorial.images):
                    file = QtCore.QFile(f'temp/{i}/memorials/{n}/images/{z}.png')
                    file.open(QtCore.QIODevice.OpenModeFlag.ReadWrite)
                    file.write(image)
                    file.close()
                await asyncio.sleep(0.2)
                self.progresslabel.setText(
                    f'Сохранение элементов пазла и их расположения мемориала {memorial.name} уровня {level[1].name}')
                s = ''
                os.mkdir(f'temp/{i}/memorials/{n}/images/puzzle')
                for p in range(len(memorial.puzzleparts)):
                    for ind, part in enumerate(memorial.puzzleparts[p]):
                        part.save(f'temp/{i}/memorials/{n}/images/puzzle/{p}_{ind}.png')
                        s += f'{p}_{ind}.png '
                    s += '\n'

                with open(f'temp/{i}/memorials/{n}/images/puzzle/matrix.txt', 'w') as f:
                    f.write(s)

            self.progressbar.setValue(int(self.progressbar.value() + pr))
        await asyncio.sleep(0.2)
        self.progresslabel.setText('Упаковка уровня в архив')
        archive = shutil.make_archive(self.dir.split('/')[-1], 'zip', str(getabspath('temp')))
        shutil.move(str(getabspath(archive)), self.dir)
        self.progressbar.setValue(100)
        self.progresslabel.setText('Готово')
        self.setLayout(self.donelout)



class DClickImgLabel(QLabel):
    clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setMouseTracking(True)
        self.setStyleSheet(imgqss)

    def mousePressEvent(self, a0):
        if self.styleSheet() == imgqss.replace("black", "red"):
            self.setStyleSheet(imgqss)
        self.clicked.emit()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Создание уровней")
        self.cw = CentralWidget()
        self.initialize()

    def initialize(self):
        self.cw.initialize()
        self.resize(1280, 720)
        self.setCentralWidget(self.cw)
        self.show()


app = QApplication([])
loop = QEventLoop(app)
asyncio.set_event_loop(loop)
window = MainWindow()
with loop:
    loop.run_forever()
