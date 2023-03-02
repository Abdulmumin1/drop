from PyQt5.QtWidgets import (QApplication, QFrame, QPushButton, QLabel, QVBoxLayout, QLineEdit,
                             QHBoxLayout, QMainWindow, QScrollArea, QCheckBox, QColorDialog, QFileDialog)
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal
from server import init_server, destroy_server, server, send_to_client, send_multiple
from utils import scroll_hor, scroll_var, save_data, load_data
import json
from client import thread, threading
cl_list = []
recievers_list = []

user_data = load_data()
if not user_data:
    user_data = {'name': 'username', 'color': 'orange'}


class Worker(QObject):
    client_data = pyqtSignal(str)

    def __init__(self, parent=None):
        QObject.__init__(self, parent=parent)
        self.continue_run = True

    def receive_msg(self):
        while self.continue_run:
            client, address = server.accept()
            cl_list.append(client)
            client.send('DATA'.encode())
            name = client.recv(1024).decode()
            self.client_data.emit(name)


class ClientHandler():
    def __init__(self):
        self.client_addresses = {}


class sendersZone(QFrame):
    def __init__(self):
        super().__init__()

        layout = QHBoxLayout(self)
        send_file_btn = QPushButton(text='Send', clicked=self.send_files)
        send_file_btn.setStyleSheet(
            '')
        layout.addWidget(send_file_btn, alignment=Qt.AlignCenter)

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
        self.setMinimumHeight(300)
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
        init_server()
        self.create_threads()
        main_frame = QFrame()
        main_layout = QVBoxLayout(main_frame)

        user_profile = UserProfile()
        self.dropzone = RecieversZone()
        sender_zone = sendersZone()
        # sender_zone.send_file_btn.connect(self.send_files)
        main_layout.addWidget(user_profile, alignment=Qt.AlignTop)
        main_layout.addWidget(self.dropzone)
        main_layout.addWidget(sender_zone)

        self.setCentralWidget(main_frame)
        thread.start()

    def create_threads(self):
        self.thread = QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.receive_msg)
        self.worker.client_data.connect(self.add_connected)
        self.thread.start()

    def add_connected(self, data):
        new = RecieversFrame(data)
        self.dropzone.r_layout.insertWidget(0, new)
        print(data)

    def closeEvent(self, a0):
        self.thread.deleteLater()
        self.worker.deleteLater()
        print(self.size().width(), self.size().height())
        destroy_server()


def run():
    app = QApplication(['Drop'])
    win = Main()
    win.show()
    app.exec_()


if __name__ == '__main__':
    run()
