import os
import sys

from PIL import Image, ImageDraw
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor, QKeyEvent
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QStackedWidget, QWidget, QHBoxLayout, QListWidget, \
    QLabel, QListWidgetItem, QVBoxLayout, QMessageBox, QFileDialog, QDialog, QLineEdit, QTextEdit

currentindexqss = """
        QLabel {
            border-radius: 5px;      /* Закругленные углы */
            font-family: "Arial";    /* Используем шрифт Arial */
            font-size: 14px;         /* Размер шрифта */
            font-weight: bold;       /* Жирный шрифт */
            background-color: blue;  /* Фон серый при наведении */
        }
        """
defaultqss = """
        QLabel {
            border-radius: 5px;      /* Закругленные углы */
            font-family: "Arial";    /* Используем шрифт Arial */
            font-size: 14px;         /* Размер шрифта */
            font-weight: bold;       /* Жирный шрифт */
        }
        
        QLabel:hover {
            background-color: gray;  /* Фон серый при наведении */
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
            background-color: #e0e0e0; /* Light gray background */
            color: black;            /* White text color */
            border: 1px solid #808080; /* Dark gray border */
            border-radius: 5px;        /* Rounded corners */
            padding: 10px 20px;        /* Padding inside the button */
            font-weight: bold;         /* Bold font for prominence */
        }
        
        QPushButton:hover {
            background-color: #c0c0c0; /* Slightly darker on hover */
        }
        
        QPushButton:pressed {
            background-color: #a0a0a0; /* Even darker on press */
        }
        """

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
            font-size: 25px;         /* Размер шрифта */
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
        self.initialize()

    def initialize(self):
        self.loadImage(getabspath("Preview.jpg"))

    def loadImage(self, path):
        self.pixmap.load(getabspath(path))
        self.imagelabel.setPixmap(self.pixmap)
        global levels
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
        self.imagelabel = ImageLabel()
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
            for pos in levels:
                pos = pos[0]
                if abs(pos.x() - local_pos.x()) < 10 and abs(pos.y() - local_pos.y()) < 10:
                    LevelRedactor(LevelData).exec()
                    return

            levels.append(tuple([local_pos, LevelData()]))
            if len(levels) > 1:
                AvInd.append(2)
            elif 2 in AvInd:
                AvInd.remove(2)
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
                    return

    def setImage(self, pixmap):
        self.imagelabel.setPixmap(pixmap)
        self.imagelabel.ispixmap = True


class ImageLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.ispixmap = False
        self.setMouseTracking(True)

    def paintEvent(self, event):
        super().paintEvent(event)
        global levels
        if not self.ispixmap: return
        if not levels: return

        painter = QPainter(self)
        painter.setPen(QColor(0, 0, 255))
        painter.setBrush(QColor(0, 0, 255))
        painter.drawEllipse(levels[0][0], 10, 10)
        painter.setPen(QColor(255, 0, 0))
        painter.setBrush(QColor(255, 0, 0))

        for pos in levels[1::]:
            pos = pos[0]
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
        self.images = []
        self.name = ''
        self.desc = ''
        self.memorials = []


class Memorial:
    def __init__(self):
        self.preview = None
        self.images = []
        self.name = ''
        self.desc = ''
        self.puzzle_parts = None


class LevelRedactor(QDialog):
    def __init__(self, LevelData):
        super().__init__()
        self.levelData = LevelData
        self.setWindowTitle("Редактирование данных уровня")
        self.resize(900, 400)
        self.nextbtn = QPushButton(text="Далее")
        self.nextbtn.setStyleSheet(buttonqss)
        self.nextbtn.setFixedSize(100,50)
        self.images = [[DClickImgLabel(), QPixmap(), False] for _ in range(4)]
        self.addImage(getabspath("add.png"))
        self.images[0][2] = False
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
        self.textlabel = QLabel(text="Загрузите фотографии обьекта 16:9, нажав на последнее добавленное изображение сверху.\n"
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

    def addImage(self, image):
        for img in self.images:
            if not img[2]:
                img[1].load(image)
                img[1] = img[1].scaled(300, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
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
        pass

class Finishing(StackedWidget):
    def __init__(self):
        super().__init__()
        self.index = 3
        self.indexes.itemWidget(self.indexes.item(self.index)).setStyleSheet(currentindexqss)
        self.nextbtn.hide()

class DClickImgLabel(QLabel):
    clicked = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.setMouseTracking(True)
        self.setStyleSheet("""
            QLabel {
                border-radius: 10px;
                border: 2px solid transparent;
                padding: 5px;
            }
            QLabel:hover {
                border-radius: 10px;
                border: 2px solid black;
                background-color: gray;
            }
        """)


    def mousePressEvent(self, a0):
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
window = MainWindow()
app.exec()
