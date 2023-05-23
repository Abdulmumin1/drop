
from PyQt5.QtWidgets import (QApplication, QFrame, QPushButton, QLabel, QVBoxLayout, QLineEdit, QListWidget,
                             QHBoxLayout, QMainWindow, QScrollArea, QCheckBox, QColorDialog, QFileDialog)
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal, pyqtProperty, QRect, QPropertyAnimation, QMimeData
from PyQt5.QtGui import QPixmap, QIcon, QColor, QDrag
from server import init_server, destroy_server, server, send_to_client, send_multiple
from utils import (scroll_hor, scroll_var, save_data,
                   load_data, generateQRCode, create_download_files, empty_download_files, return_file_basename)
import json
# from client import client_thread, threading
from flask_server import flask_Server, get_devices, server_thread, kill_server
import os

cl_list = []
recievers_list = []

user_data = load_data()
if not user_data:
    user_data = {'name': 'username', 'color': 'orange'}


class Worker(QObject):
    client_data = pyqtSignal(str)

    def __init__(self, parent=None):
        QObject.__init__(self, parent=parent)
        # flask_Server('k')
        self.continue_run = True

    def start_flask_server(self):
        flask_Server('param')

    # def receive_msg(self):

    #     while self.continue_run:
    #         print('greadt')
    #         # client, address = server.accept()
    #         # cl_list.append(client)
    #         # client.send('DATA'.encode())
    #         # name = client.recv(1024).decode()
    #         # self.client_data.emit(name)


class ClientHandler():
    def __init__(self):
        self.client_addresses = {}


class PopButton(QPushButton):
    def __init__(self, text, clicked, parent=None):
        super(PopButton, self).__init__(parent)
        self.setText(text)
        self.clicked_function = clicked

    def mousePressEvent(self, e):
        self.animate()

    def animate(self):
        self.anim = QPropertyAnimation(self, b'color')
        self.anim.setStartValue(QColor(255, 255, 255))
        self.anim.setEndValue(QColor(0, 0, 0))
        self.anim.setDuration(300)

        # Scale up the button
        self.anim2 = QPropertyAnimation(self, b'geometry')
        self.anim2.setDuration(200)
        self.anim2.setStartValue(
            QRect(self.x(), self.y(), self.width(), self.height()))
        self.anim2.setEndValue(QRect(self.x()-5, self.y()-5,
                                     self.width()+10, self.height()+10))

        # Scale down the button
        self.anim3 = QPropertyAnimation(self, b'geometry')
        self.anim3.setDuration(100)
        self.anim3.setStartValue(QRect(self.x()-5, self.y()-5,
                                       self.width()+10, self.height()+10))
        self.anim3.setEndValue(
            QRect(self.x(), self.y(), self.width(), self.height()))

        self.anim.start()
        self.anim2.start()
        self.anim3.start()
        self.anim3.finished.connect(self.clicked_function)

    def getColor(self):
        return self.palette().color(self.backgroundRole())

    def setColor(self, color):
        palette = self.palette()
        palette.setColor(self.backgroundRole(), color)
        self.setPalette(palette)

    color = pyqtProperty(QColor, getColor, setColor)


def make_button(text, clicked, parent):
    but = PopButton(text, clicked=clicked, parent=parent)
    but.setStyleSheet(
        f'background:{user_data["color"]}; padding:6px; border:0; border-radius:3px;')
    but.setCursor(Qt.PointingHandCursor)
    return but


class DropFrame(QFrame):
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(200)

        self.setAcceptDrops(True)
        self.label = QLabel('<h2>Files</h2>\n<em>Drop files here</em>')
        self.listbox = QListWidget()
        selected_color = 'QListWidget::item:selected{background:' + \
            f'{user_data["color"]};'+'border:0; padding:3px;}'
        self.listbox.setStyleSheet(
            scroll_var+scroll_hor+'QListWidget{border-radius:2px; padding:2px; border:10px solid '+f'{user_data["color"]}'+';}'+selected_color)

        self.file_frame = QFrame()
        self.file_frame_layout = QVBoxLayout(self.file_frame)
        scroll_area = QScrollArea()
        scroll_area.setStyleSheet(
            "QScrollArea{border:1.5px solid "+user_data['color']+"; border-radius:4px;}"+scroll_hor+scroll_var)
        scroll_area.setWidgetResizable(True)

        # scroll_area.horizontalScrollBar().setDisabled(True)
        scroll_area.setWidget(self.file_frame)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.addWidget(self.label)
        self.main_layout.addWidget(scroll_area)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        l = []
        for url in event.mimeData().urls():
            l.append(url.toLocalFile())
        create_download_files(l)
        self.addItems(return_file_basename(l))

    def addItems(self, items):
        for i in items:
            self.file_frame_layout.addWidget(self.file_label(i))

    def file_label(self, txt):
        label = QLabel(txt)
        label.setStyleSheet('padding:4px; font-size:11px;')
        return label


class MobileQrFrame(QFrame):
    def __init__(self):
        super().__init__()

        self.qr_showed = False
        # self.setMinimumHeight(300)
        # self.setStyleSheet('background:orange;')
        self.file_ = None
        self.selected_files_listbox = DropFrame()
        main_layout = QVBoxLayout(self)
        layout = QHBoxLayout()
        self.qr_image = QLabel()
        self.qr_image.hide()
        self.ip_label = QLabel()

        # layout.addWidget(self.qr_image)
        # qr_image.setPixmap()
        select_file_btn = make_button(
            text='select files', clicked=self.select_files, parent=self)

        layout.addWidget(select_file_btn)

        # generateQRCode = make_button(
        #     text='Generate QR', clicked=self.genereate_qr_code)

        # layout.addWidget(generateQRCode, alignment=Qt.AlignCenter)

        self.back_btn = make_button(
            text='Show QRCode', clicked=self.show_files, parent=self)

        layout.addWidget(self.back_btn)
        main_layout.addStretch()
        main_layout.addWidget(self.qr_image, alignment=Qt.AlignCenter)
        main_layout.addWidget(self.selected_files_listbox, Qt.AlignCenter)
        main_layout.addWidget(self.ip_label, alignment=Qt.AlignCenter)
        self.selected_files_listbox.hide()
        main_layout.addLayout(layout)

    def select_files(self):
        file_names = QFileDialog.getOpenFileNames(
            self.parent(), 'upload file')
        if file_names[0]:
            try:
                empty_download_files()
            except:
                pass
            create_download_files(file_names[0])
            self.file_ = True

            self.selected_files_listbox.addItems(
                return_file_basename(file_names[0]))

    def genereate_qr_code(self):
        # if not self.file_:
        #     return
        # self.qr_image.show()
        self.selected_files_listbox.show()
        ip = get_devices()
        ip = ip if ip else '127.0.0.1'
        self.ip_label.setText(f'http://{ip}:5000')
        generateQRCode(ip)
        self.qr_image.setPixmap(QPixmap('qr.png'))
        # sthread = threading.Thread(
        #     target=flask_Server, args=(self.file_,))
        # sthread.start()
        # server_thread.start()

        print('thread-started')

    def show_files(self):
        if self.qr_showed:
            self.selected_files_listbox.show()
            self.qr_image.hide()
            self.qr_showed = False
            self.back_btn.setText('Show QRCode')
            return
        self.selected_files_listbox.hide()
        self.qr_image.show()
        self.qr_showed = True
        self.back_btn.setText('Files')

    def animate(self):
        self.animation.start()


class sendersZone(QFrame):
    def __init__(self):
        super().__init__()

        layout = QHBoxLayout(self)
        send_file_btn = QPushButton(text='Send', clicked=self.send_files)
        send_file_btn.setStyleSheet(
            '')
        layout.addWidget(send_file_btn, alignment=Qt.AlignCenter)

        self.send_to_mobile_btn = QPushButton(
            text='Mobile')
        self.send_to_mobile_btn.setStyleSheet(
            '')
        layout.addWidget(self.send_to_mobile_btn, alignment=Qt.AlignCenter)

        add_friend_btn = QPushButton(
            text='Add Friend')
        add_friend_btn.setStyleSheet(
            '')
        layout.addWidget(add_friend_btn, alignment=Qt.AlignCenter)

    def send_files(self):
        print('send files clicked')
        # file_dialog = QFileDialog()

        # file_dialog.open()
        file_names = QFileDialog.getOpenFileNames(
            self.parent().parent(), 'upload file')
        if file_names[0]:
            print(file_names[0])
            for al_cl in recievers_list:
                al_cl.send('FILE'.encode('ascii'))

                thread = threading.Thread(target=send_multiple, args=(
                    al_cl, file_names[0]))
                thread.start()


class RecieversFrame(QFrame):
    def __init__(self, data):
        super().__init__()
        self.id = len(cl_list)-1
        data = json.loads(data)
        # print(data)
        self.transferGroup = False
        layout = QHBoxLayout(self)
        frame = QFrame()
        frame.setFixedHeight(30)
        frame.setFixedWidth(30)
        frame.setStyleSheet(
            f'border-radius:15px; background:{data["color"]};')
        label = QLabel(data['name'])
        self.btn = QPushButton(text='🔗', clicked=self.button_func)
        layout.addWidget(frame)
        layout.addWidget(label)
        layout.addStretch()
        layout.addWidget(self.btn)

    def button_func(self):
        if not self.transferGroup:
            recievers_list.append(cl_list[self.id])
            self.btn.setText('disconnect')
            self.transferGroup = True
        else:
            recievers_list.remove(cl_list[self.id])
            self.btn.setText('🔗')
            self.transferGroup = False
        # self.btn.setEnabled = False


class RecieversZone(QFrame):
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(20)
        layout = QVBoxLayout(self)
        label = QLabel('<h2>Available</h2>')
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet(
            '')
        self.receivers_frame = QFrame()
        self.r_layout = QVBoxLayout(self.receivers_frame)
        scroll_area = QScrollArea()
        scroll_area.setStyleSheet(
            "QScrollArea{border:0px;}"+scroll_hor+scroll_var)
        scroll_area.setWidgetResizable(True)

        # scroll_area.horizontalScrollBar().setDisabled(True)
        scroll_area.setWidget(self.receivers_frame)
        layout.addWidget(label, alignment=Qt.AlignTop)
        layout.addWidget(scroll_area)
        self.r_layout.addStretch(1)
        self.setStyleSheet(
            'QFrame{}')


class UserData():
    def __init__(self):
        self.name = 'user'
        self.ip = 'default'
        self.color = 'orange'


class BGImage(QFrame):
    def __init__(self, usercolor):
        super().__init__()
        self.setFixedHeight(100)
        self.setFixedWidth(100)
        self.setStyleSheet(
            'QFrame{border-radius:50%;' + f'background:{usercolor}'+'}')
        self.sstext = QLabel('Change')
        self.layoutF = QVBoxLayout(self)
        self.layoutF.addStretch()
        self.layoutF.addWidget(self.sstext, alignment=Qt.AlignCenter)
        self.layoutF.addStretch()
        self.sstext.hide()

    def mouseReleaseEvent(self, a0):
        if not self.parent().editing:
            return
        colordlg = QColorDialog.getColor()
        if colordlg.isValid():
            new_color = colordlg.name()
            user_data['color'] = new_color
            self.setStyleSheet(
                'QFrame{border-radius:50%;' + f'background:{new_color}'+'}')


class UserProfile(QFrame):
    def __init__(self):
        super().__init__()
        self.editing = False
        usercolor, username = user_data['color'], user_data['name']
        layout = QVBoxLayout(self)
        self.image = BGImage(usercolor)
        self.name = QLabel(username)
        self.edit_name = QPushButton(text='edit', clicked=self.btn_func)
        self.name_input = QLineEdit()
        self.name_input.hide()
        layout.addStretch()
        layout.addWidget(self.image, alignment=Qt.AlignCenter)
        layout.addWidget(self.name, alignment=Qt.AlignCenter)
        layout.addWidget(self.name_input, alignment=Qt.AlignCenter)
        layout.addWidget(self.edit_name, alignment=Qt.AlignCenter)
        layout.addStretch()

    def btn_func(self):
        if self.editing:
            self.editing = False
            new_name = self.name_input.text()
            self.name.show()
            self.edit_name.setText('edit')
            self.name_input.hide()
            self.name.setText(new_name)
            self.image.sstext.hide()
            save_data(new_name, user_data['color'])
        else:
            self.editing = True
            self.name.hide()
            self.edit_name.setText('save')
            self.name_input.show()
            self.image.sstext.show()
            self.name_input.setText(self.name.text())


class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedHeight(500)
        self.setFixedWidth(330)

        self.setWindowIcon(QIcon('drop_icon.png'))
        # init_server()
        # self.create_threads()
        main_frame = QFrame()
        main_layout = QVBoxLayout(main_frame)

        user_profile = UserProfile()
        self.dropzone = RecieversZone()
        self.dropzone.hide()
        self.mobile_zone = MobileQrFrame()
        main_layout.addWidget(user_profile, alignment=Qt.AlignTop)
        main_layout.addWidget(self.dropzone)
        main_layout.addWidget(self.mobile_zone)

        self.setCentralWidget(main_frame)
        self.mobile_zone.genereate_qr_code()
        self.showEvent = self.startup_events

        # self.mobile_zone.genereate_qr_code()

    def startup_events(self, e):
        self.create_threads()

    def create_threads(self):
        self.thread = QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.thread)
        # self.thread.started.connect(self.worker.receive_msg)
        self.thread.started.connect(self.worker.start_flask_server)
        self.worker.client_data.connect(self.add_connected)
        self.thread.start()

    def add_connected(self, data):
        new = RecieversFrame(data)
        self.dropzone.r_layout.insertWidget(0, new)
        print(data)

    def closeEvent(self, a0):
        empty_download_files()

        kill_server()


def run():
    app = QApplication(['Drop'])
    win = Main()
    win.show()
    app.exec_()


if __name__ == '__main__':
    run()
    # server_thread.join()
