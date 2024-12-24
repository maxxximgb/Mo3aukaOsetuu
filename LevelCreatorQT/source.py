import os
import sys

from PIL import Image, ImageDraw
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor, QKeyEvent
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QStackedWidget, QWidget, QHBoxLayout, QListWidget, \
    QLabel, QListWidgetItem, QVBoxLayout, QMessageBox, QFileDialog

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

AvInd = [1]
dotpos = []
levelconfs = []

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
        self.indexes.setMinimumSize(190, 250)
        self.nextbtn = QPushButton(self)
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
        self.loadImage("Preview.jpg")

    def loadImage(self, path):
        self.pixmap.load(getabspath(path))
        self.imagelabel.setPixmap(self.pixmap)
        global dotpos
        dotpos.clear()

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
            global dotpos
            for pos in dotpos:
                if abs(pos.x() - local_pos.x()) < 10 and abs(pos.y() - local_pos.y()) < 10:
                    return

            dotpos.append(local_pos)
            if len(dotpos) > 1: AvInd.append(2)
            elif 2 in AvInd: AvInd.remove(2)
            self.imagelabel.update()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete:
            global dotpos
            mouse_pos = self.imagelabel.mapFromGlobal(self.cursor().pos())
            for pos in dotpos:
                if abs(pos.x() - mouse_pos.x()) < 10 and abs(pos.y() - mouse_pos.y()) < 10:
                    dotpos.remove(pos)
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
        global dotpos
        if not self.ispixmap: return
        if not dotpos: return

        painter = QPainter(self)
        painter.setPen(QColor(0, 0, 255))
        painter.setBrush(QColor(0, 0, 255))
        painter.drawEllipse(dotpos[0], 10, 10)
        painter.setPen(QColor(255, 0, 0))
        painter.setBrush(QColor(255, 0, 0))

        for pos in dotpos[1::]:
            painter.drawEllipse(pos, 10, 10)

    def mouseMoveEvent(self, event):
        global dotpos
        mouse_pos = self.mapFromGlobal(self.cursor().pos())
        for pos in dotpos:
            if abs(pos.x() - mouse_pos.x()) < 10 and abs(pos.y() - mouse_pos.y()) < 10:
                self.setCursor(Qt.CursorShape.PointingHandCursor)
                return

        self.setCursor(Qt.CursorShape.ArrowCursor)


class ConfiguringLevels(QWidget):
    def __init__(self):
        super().__init__()


class Finishing(StackedWidget):
    def __init__(self):
        super().__init__()
        self.index = 3
        self.indexes.itemWidget(self.indexes.item(self.index)).setStyleSheet(currentindexqss)
        self.nextbtn.hide()


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
