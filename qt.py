import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, \
    QListWidget, QFileDialog, QSplitter
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QSize
from PyQt5.uic import loadUi
class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = loadUi('designer1.ui', self)
        max_label_size = QSize(600, 600)
        # Обработчик нажатия на кнопку "Загрузить данные"
        def load_data_button_clicked():
            options = QFileDialog.Options()
            options |= QFileDialog.ReadOnly
            files, _ = QFileDialog.getOpenFileNames(self.ui.centralWidget, "Выберите фотографии", "",
                                                    "Images (*.jpg *.png *.bmp *.jpeg);;All Files (*)", options=options)
            if files:
                self.ui.photoListWidget.clear()
                self.ui.photoListWidget.show()
                self.ui.stackedWidget.setCurrentIndex(1)
                for file in files:
                    filename = os.path.abspath(file)
                    self.ui.photoListWidget.addItem(filename)
                    self.ui.startButton.hide()

                self.ui.countLabel.setText(str(self.ui.photoListWidget.count()))
        # Обработчик выбора фотографии из списка
        def photo_list_item_clicked(item):
            selected_photo_path = os.path.abspath(item.text())
            pixmap = QPixmap(selected_photo_path)
            pixmap = pixmap.scaled(max_label_size, Qt.KeepAspectRatio)
            self.ui.photoDisplayLabel.setPixmap(pixmap)
            self.ui.photoDisplayLabel.show()

        self.ui.startButton.clicked.connect(load_data_button_clicked)


        self.ui.photoListWidget.itemClicked.connect(photo_list_item_clicked)

        # Показываем основное окно


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())