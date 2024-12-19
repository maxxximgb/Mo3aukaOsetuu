from PIL import Image, ImageDraw
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QStackedWidget, QWidget, QHBoxLayout, QListWidget, \
    QLabel, QListWidgetItem


class CentralWidget(QStackedWidget):
    def __init__(self):
        super().__init__()

    def initialize(self):
        self.addWidget(StackedWidget())

class StackedWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.index = -1
        self.lout = QHBoxLayout()
        self.indexes = QListWidget()
        self.indexes.setSpacing(15)
        self.addItemToList(QLabel("Начало"))
        self.addItemToList(QLabel("Загрузка карты"))
        self.addItemToList(QLabel("Создание уровней"))
        self.addItemToList(QLabel("Настройка уровней"))
        self.addItemToList(QLabel("Сохранение"))
        self.lout.addWidget(self.indexes)
        self.setLayout(self.lout)

    def addItemToList(self, a):
        a.setStyleSheet("""
        QLabel {
            color: white;            /* Цвет текста белый */
            border-radius: 5px;      /* Закругленные углы */
            font-family: "Arial";    /* Используем шрифт Arial */
            font-size: 14px;         /* Размер шрифта */
            font-weight: bold;       /* Жирный шрифт */
        }
        
        QLabel:hover {
            background-color: gray;  /* Фон серый при наведении */
        }
        """)
        item = QListWidgetItem()
        self.indexes.addItem(item)
        self.indexes.setItemWidget(item, a)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
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
