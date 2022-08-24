from __future__ import unicode_literals
import youtube_dl as youtube
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QFileDialog, QButtonGroup, QMessageBox
from PyQt5.QtCore import Qt
import interface_ui
from os.path import expanduser
import threading
from hurry.filesize import size
import configparser
import win10toast


# import os
# SAVE_PATH = '/'.join(os.getcwd().split('/')[:3]) + '/Downloads'


class Logger(object):

    def debug(self, msg):
        print('debug', msg)

    def warning(self, msg):
        print('warning', msg)

    def error(self, msg):
        print('error', msg)


PATH = ''
try:
    settings = configparser.ConfigParser()
    settings.read('settings.ini')
    PATH = settings['SETTINGS']['path']
except FileNotFoundError:
    PATH = ''

video_format = ''  # [best, worst, bestvideo, worstvideo, bestaudio, worstaudio]
all_choose = []
status = ''
toaster = win10toast.ToastNotifier()


class VideoDownloader(QtWidgets.QMainWindow, interface_ui.Ui_MainWindow, threading.Thread):
    settings = configparser.ConfigParser()
    settings.read('settings.ini')

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        threading.Thread.__init__(self)

        self.link = ''

        self.light_theme_check = None
        self.dark_theme_check = None
        self.get_config()
        self.label_4.setText(PATH)

        self.options = {
            'format': video_format,
            'logger': Logger(),
            'progress_hooks': [self.progress],
            'outtmpl': f'{PATH}/%(title)s.%(ext)s',  # + '/%(title)s.%(ext)s'
        }

        self.pushButton_2.pressed.connect(self.get_path)
        self.pushButton.pressed.connect(self.start_thread)
        self.pushButton_4.clicked.connect(self.message_box)

        # Прибираємо стандартні рамки вікна
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.center()

        self.pushButton_3.clicked.connect(lambda: self.close())
        self.pushButton_5.clicked.connect(lambda: self.showMinimized())
        self.pushButton_6.clicked.connect(self.change_theme)

        # встановлюємо icon.ico в треї програми
        self.setWindowIcon(QtGui.QIcon('icon.ico'))

        self.checkBox.stateChanged.connect(self.state_changed_checkbox)  # audio
        self.checkBox_2.stateChanged.connect(self.state_changed_box)  # video

        self.button_format = {
            self.radioButton: 'bestvideo',
            self.radioButton_2: 'worstvideo',
            self.radioButton_3: 'bestaudio',
            self.radioButton_4: 'worstaudio'
        }

        # self.radioButton.setChecked(True)
        self.button_group_1 = QButtonGroup()
        self.button_group_1.addButton(self.radioButton)
        self.button_group_1.addButton(self.radioButton_2)
        self.button_group_1.buttonClicked.connect(self.get_text_from_radiobutton)

        # self.radioButton_3.setChecked(True)
        self.button_group_2 = QButtonGroup()
        self.button_group_2.addButton(self.radioButton_3)
        self.button_group_2.addButton(self.radioButton_4)
        self.button_group_2.buttonClicked.connect(self.get_text_from_radiobutton_2)

    # Переміщення вікна без рамок
    # ==================================================================
    def center(self):
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        try:
            delta = QtCore.QPoint(event.globalPos() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPos()
        except AttributeError:
            pass

    # ==================================================================

    def reload_config(self):
        VideoDownloader.settings = configparser.ConfigParser()
        VideoDownloader.settings.read('settings.ini')

    def get_config(self):
        theme = VideoDownloader.settings['SETTINGS']['theme']
        if theme == 'LIGHT':
            self.light_theme()
            self.light_theme_check = True
            self.dark_theme_check = False
        elif theme == 'DARK':
            self.dark_theme()
            self.light_theme_check = False
            self.dark_theme_check = True

    def change_theme(self):
        self.reload_config()
        if self.light_theme_check:
            self.dark_theme()
            self.light_theme_check = False
            self.dark_theme_check = True

            with open('settings.ini', 'r') as f:
                old = f.read()
            get_old_theme = VideoDownloader.settings['SETTINGS']['theme']
            new_theme = 'DARK'
            new = old.replace(get_old_theme, new_theme)
            with open('settings.ini', 'w') as f:
                f.write(new)

        elif self.dark_theme_check:
            self.light_theme()
            self.light_theme_check = True
            self.dark_theme_check = False

            with open('settings.ini', 'r') as f:
                old = f.read()
            get_old_theme = VideoDownloader.settings['SETTINGS']['theme']
            new_theme = 'LIGHT'
            new = old.replace(get_old_theme, new_theme)
            with open('settings.ini', 'w') as f:
                f.write(new)

            with open('settings.ini', 'r') as f:
                old = f.read()
            get_old_theme = VideoDownloader.settings['SETTINGS']['theme']
            new_theme = 'LIGHT'
            new = old.replace(get_old_theme, new_theme)
            with open('settings.ini', 'w') as f:
                f.write(new)

    def dark_theme(self):
        self.progressBar.setStyleSheet("QProgressBar{\n"
                                       "background-color: #6e6e6e;\n"
                                       "border-radius: 10px;\n"
                                       "color: white;\n"
                                       "}\n"
                                       "QProgressBar::chunk{\n"
                                       "background-color: qlineargradient(spread:reflect, x1:0, y1:0.483, x2:1, y2:0.483136, stop:0 rgba(89, 95, 118, 255), stop:1 rgba(44, 49, 60, 255));\n"
                                       "    border-radius: 10px;\n"
                                       "}")
        self.frame.setStyleSheet("QFrame{\n"
                                 "border-radius: 7px;\n"
                                 "background-color: #1B1D23;\n"
                                 "}")
        self.frame_3.setStyleSheet("QFrame{\n"
                                   "border-bottom-left-radius: 0px;\n"
                                   "border-bottom-right-radius: 0px;\n"
                                   "background-color: #2C313C;\n"
                                   "}")
        self.frame_4.setStyleSheet("QFrame{\n"
                                   "color: white;\n"
                                   "border-radius: 7px;\n"
                                   "background-color: #2C313C;\n"
                                   "}")
        self.radioButton.setStyleSheet("color: #ffffff;")
        self.radioButton_2.setStyleSheet("color: #ffffff;")
        self.radioButton_3.setStyleSheet("color: #ffffff;")
        self.radioButton_4.setStyleSheet("color: #ffffff;")
        self.pushButton.setStyleSheet("QPushButton{\n"
                                      "color: white;\n"
                                      "border-radius: 7px;\n"
                                      "background-color: #595F76;\n"
                                      "}\n"
                                      "\n"
                                      "QPushButton:hover{\n"
                                      "background-color: #50566E;\n"
                                      "}\n"
                                      "\n"
                                      "QPushButton:pressed{\n"
                                      "background-color: #434965;\n"
                                      "}")
        self.pushButton_2.setStyleSheet("QPushButton{\n"
                                        "color: white;\n"
                                        "border-radius: 7px;\n"
                                        "background-color: #595F76;\n"
                                        "}\n"
                                        "\n"
                                        "QPushButton:hover{\n"
                                        "background-color: #50566E;\n"
                                        "}\n"
                                        "\n"
                                        "QPushButton:pressed{\n"
                                        "background-color: #434965;\n"
                                        "}")
        self.pushButton_3.setStyleSheet("QPushButton{\n"
                                        "color: white;\n"
                                        "border: none;\n"
                                        "border-top-right-radius: 7px;\n"
                                        "background-color: #2C313C;\n"
                                        "}\n"
                                        "\n"
                                        "QPushButton:hover{\n"
                                        "background-color: #45494D;\n"
                                        "}\n"
                                        "\n"
                                        "QPushButton:pressed{\n"
                                        "color: #EA2F4E;\n"
                                        "}")
        self.pushButton_4.setStyleSheet("QPushButton{\n"
                                        "color: white;\n"
                                        "border-radius: 19px;\n"
                                        "background-color: #595F76;\n"
                                        "}\n"
                                        "\n"
                                        "QPushButton:hover{\n"
                                        "background-color: #50566E;\n"
                                        "}\n"
                                        "\n"
                                        "QPushButton:pressed{\n"
                                        "background-color: #434965;\n"
                                        "}")
        self.pushButton_5.setStyleSheet("QPushButton{\n"
                                        "color: white;\n"
                                        "border: none;\n"
                                        "border-top-right-radius: 7px;\n"
                                        "background-color: #2C313C;\n"
                                        "}\n"
                                        "\n"
                                        "QPushButton:hover{\n"
                                        "background-color: #45494D;\n"
                                        "}\n"
                                        "\n"
                                        "QPushButton:pressed{\n"
                                        "    color: #EA2F4E;\n"
                                        "}")
        self.pushButton_6.setStyleSheet("QPushButton{\n"
                                        "color: white;\n"
                                        "border-radius: 7px;\n"
                                        "background-color: #595F76;\n"
                                        "}\n"
                                        "\n"
                                        "QPushButton:hover{\n"
                                        "background-color: #50566E;\n"
                                        "}\n"
                                        "\n"
                                        "QPushButton:pressed{\n"
                                        "background-color: #434965;\n"
                                        "}")
        self.lineEdit.setStyleSheet("QLineEdit{\n"
                                    "    border-radius: 7px;\n"
                                    "}")
        self.checkBox.setStyleSheet("color: #ffffff;")
        self.checkBox_2.setStyleSheet("color: #ffffff;")
        self.label_2.setStyleSheet("color: #ffffff;")
        self.label_3.setStyleSheet("color: #ffffff;")
        self.label_4.setStyleSheet("color: #ffffff;")
        self.label_5.setStyleSheet("color: #ffffff;")
        self.label_6.setStyleSheet("color: #ffffff;")

    def light_theme(self):
        self.progressBar.setStyleSheet("""QProgressBar{background-color: #6e6e6e; border-radius: 10px; color: #000000;}
                                           QProgressBar::chunk{
                                           background-color: qlineargradient(spread:reflect, x1:0, y1:0.523, x2:1, y2:0.517, stop:0.131579 rgba(84, 84, 99, 255), stop:0.868421 rgba(167, 167, 167, 255)); 
                                           border-radius: 10px;}""")
        self.radioButton.setStyleSheet("background-color: #e3e3e3; color: #000000;")
        self.radioButton_2.setStyleSheet("background-color: #e3e3e3; color: #000000;")
        self.radioButton_3.setStyleSheet("background-color: #e3e3e3; color: #000000;")
        self.radioButton_4.setStyleSheet("background-color: #e3e3e3; color: #000000;")
        self.checkBox.setStyleSheet("background-color: #e3e3e3; color: #000000;")
        self.checkBox_2.setStyleSheet("background-color: #e3e3e3; color: #000000;")
        self.label_2.setStyleSheet("color: #000000;")
        self.label_3.setStyleSheet("color: #000000;")
        self.label_4.setStyleSheet("color: #000000;")
        self.label_5.setStyleSheet("color: #000000;")
        self.label_6.setStyleSheet("color: #000000;")
        self.frame.setStyleSheet("background-color: #f2f0f2; border-radius: 7px;")
        self.frame_3.setStyleSheet(
            "background-color: #9e9e9e; 	border-bottom-left-radius: 0px; border-bottom-right-radius: 0px;")
        self.frame_4.setStyleSheet("background-color: #e3e3e3")
        self.lineEdit.setStyleSheet("background-color: #d1d1d1; color: #000000;")
        self.pushButton.setStyleSheet("""QPushButton {background-color: #8a8a8a; border-radius: 7px; color: #000000;}
                                           QPushButton:hover {background-color: #737373; color: #000000;}
                                           QPushButton:pressed {background-color: #666; color: #000000;}""")
        self.pushButton_2.setStyleSheet("""QPushButton {background-color: #8a8a8a; border-radius: 7px; color: #000000;}
                                           QPushButton:hover {background-color: #737373; color: #000000;}
                                           QPushButton:pressed {background-color: #666; color: #000000;}""")
        self.pushButton_3.setStyleSheet("""QPushButton {border: none; border-top-right-radius: 7px; 
                                           background-color: #9e9e9e; color: #000000;}
                                           QPushButton:hover {background-color: #737373;}
                                           QPushButton:pressed {background-color: #666; color: #EA2F4E;}""")
        self.pushButton_4.setStyleSheet("""QPushButton {background-color: #8a8a8a; border-radius: 19px; color: #000000;}
                                           QPushButton:hover {background-color: #737373; color: #000000;}
                                           QPushButton:pressed {background-color: #666; color: #000000;}""")
        self.pushButton_5.setStyleSheet("""QPushButton {border: none; border-top-right-radius: 7px; 
                                           background-color: #9e9e9e; color: #000000;}
                                           QPushButton:hover {background-color: #737373;}
                                           QPushButton:pressed {background-color: #666; color: #EA2F4E;}""")
        self.pushButton_6.setStyleSheet("""QPushButton {background-color: #8a8a8a; border-radius: 7px; color: #000000;}
                                                   QPushButton:hover {background-color: #737373; color: #000000;}
                                                   QPushButton:pressed {background-color: #666; color: #000000;}""")

    def message_box(self):
        QMessageBox.information(self, 'Про програму',
                                'Програма для завантаження відео/аудіо з платформи youtube.com\n\nАвтор: Neor\nВерсія: 1.1')

    def get_text_from_radiobutton(self, button):
        try:
            if self.button_format[button] == 'bestvideo':
                for i in range(len(all_choose)):
                    if all_choose[i] == 'worstvideo':
                        del all_choose[i]

            if self.button_format[button] == 'worstvideo':
                for i in range(len(all_choose)):
                    if all_choose[i] == 'bestvideo':
                        del all_choose[i]
            all_choose.append(self.button_format[button])
        except Exception:
            pass

    def get_text_from_radiobutton_2(self, button):
        try:
            if self.button_format[button] == 'bestaudio':
                for i in range(len(all_choose)):
                    if all_choose[i] == 'worstaudio':
                        del all_choose[i]

            if self.button_format[button] == 'worstaudio':
                for i in range(len(all_choose)):
                    if all_choose[i] == 'bestaudio':
                        del all_choose[i]

            all_choose.append(self.button_format[button])
        except Exception:
            pass

    def state_changed_checkbox(self, state):  # audio
        global status
        if state == Qt.Checked:
            self.checkBox_2.setCheckState(False)
            self.radioButton.setEnabled(False)
            self.radioButton_2.setEnabled(False)
            status = 'audio'
            self.button_group_2.buttonClicked.connect(self.get_text_from_radiobutton_2)
            try:
                for i in range(len(all_choose)):

                    if all_choose[i] == 'bestvideo':
                        del all_choose[i]
                    if all_choose[i] == 'worstvideo':
                        del all_choose[i]

            except Exception:
                pass
        else:
            self.radioButton.setEnabled(True)
            self.radioButton_2.setEnabled(True)
            status = ''
            try:
                for i in range(len(all_choose)):
                    if all_choose[i] == 'bestaudio':
                        del all_choose[i]
                        all_choose.append('best')
                    if all_choose[i] == 'worstaudio':
                        del all_choose[i]
                        all_choose.append('worst')
            except Exception:
                pass

    def state_changed_box(self, state):  # video
        global status
        if state == Qt.Checked:
            self.checkBox.setCheckState(False)
            self.radioButton_3.setEnabled(False)
            self.radioButton_4.setEnabled(False)
            status = 'video'
            self.button_group_1.buttonClicked.connect(self.get_text_from_radiobutton)
            try:
                for i in range(len(all_choose)):
                    if all_choose[i] == 'bestaudio':
                        del all_choose[i]
                    if all_choose[i] == 'worstaudio':
                        del all_choose[i]
            except Exception:
                pass
        else:
            status = ''
            self.radioButton_3.setEnabled(True)
            self.radioButton_4.setEnabled(True)
            try:
                for i in range(len(all_choose)):
                    if all_choose[i] == 'bestvideo':
                        del all_choose[i]
                        all_choose.append('best')
                    if all_choose[i] == 'worstvideo':
                        del all_choose[i]
                        all_choose.append('worst')
            except Exception:
                pass

    def get_path(self):
        global PATH
        file_path = QFileDialog.getExistingDirectory(self, "Обрати папку", expanduser("~"), QFileDialog.ShowDirsOnly)
        self.label_4.setText(file_path)
        PATH = file_path
        self.options['outtmpl'] = f'{PATH}/%(title)s.%(ext)s'

        with open('settings.ini', 'r') as f:
            old = f.read()

        check_settings = configparser.ConfigParser()
        check_settings.read('settings.ini')
        get_old_path = check_settings['SETTINGS']['path']
        theme = check_settings['SETTINGS']['theme']

        input_settings = f"[SETTINGS]\npath = {PATH}\ntheme = {theme}"
        with open('settings.ini', 'w') as f:
            f.write(input_settings)

    def progress(self, task):
        total = task["total_bytes"]
        downloaded = task["downloaded_bytes"]
        # print(f"Total and Downloaded: {total} {downloaded}")
        self.progressBar.setMaximum(int(total))  # Проблема с прогрессбаром в процентах при выборе только аудио/видео
        self.progressBar.setValue(int(downloaded))
        self.label_6.setText(f'Завантажено: {size(downloaded)} из {size(total)}')
        if task['status'] != 'downloading':
            toaster.show_toast("YouTube Downloader", "Завантаження успішно завершено!", duration=10, threaded=True,
                               icon_path='icon.ico')
            self.label_5.setText('Завантаження відео завершено!')

    def start_thread(self):
        try:
            thread = threading.Thread(target=self.download, args=())
            thread.start()
        except Exception:
            self.label_5.setText('Сталася помилка, повторіть спробу')

    def download(self):
        self.label_5.setText('')
        global video_format
        self.link = self.lineEdit.text()  # Ссылка на видео
        if len(self.link) == 0:
            self.label_5.setText('Введіть посилання!')
            return
        if len(all_choose) == 0:
            self.label_5.setText('Оберіть якість!')
            return

        if status == 'audio':
            for i in range(len(all_choose)):
                if all_choose[i] == 'bestaudio' or all_choose[i] == 'worstaudio':
                    video_format = all_choose[i]
                    self.options['format'] = video_format
            # [best, worst, bestvideo, worstvideo, bestaudio, worstaudio]
        elif status == 'video':
            for i in range(len(all_choose)):
                if all_choose[i] == 'bestvideo':
                    video_format = 'bestvideo'
                elif all_choose[i] == 'worstvideo':
                    video_format = 'worstvideo'
            self.options['format'] = video_format
        else:
            for i in range(len(all_choose)):
                if all_choose[i] == 'bestvideo' or all_choose[i] == 'best':
                    video_format = 'best'
                    self.options['format'] = video_format
                elif all_choose[i] == 'worstvideo':
                    video_format = 'worst'
                    self.options['format'] = video_format

        try:
            with youtube.YoutubeDL(self.options) as yt:
                # print(f'{PATH}/%(title)s.%(ext)s')
                if PATH == '':
                    self.label_5.setText('Оберіть папку!')
                    return
                # self.label_5.setText('Загрузка...')
                yt.download([self.link])
                # self.progressBar.setValue()
        except Exception:
            self.label_5.setText('Виникла помилка! Повторіть спробу!')


if __name__ == '__main__':
    App = QtWidgets.QApplication([])
    window = VideoDownloader()
    window.show()
    App.exec()
