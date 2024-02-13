from flask import Flask, render_template, send_file, request
from utils import load_data, read_download_files, retrieve_files
from io import BytesIO
from zipfile import ZipFile
import socket
import os
import sys
import re
import threading


def flask_Server(l):
    data = load_data()
    name, color = 'username', 'orange'
    if data:
        name = data['name']
        color = data['color']
    app = Flask(__name__)

    @app.route('/')
    def index():
        local_files = read_download_files()
        l = retrieve_files()
        # path_and_name = [map(lambda x:os.path.basename(x), local_files)]
        # print(path_and_name)
        return render_template('index.html', sender=name, color=color, links=local_files, l=l)

    @app.route('/download')
    def download_file():
        local_files = retrieve_files()
        if len(local_files) > 1:
            files = BytesIO()
            with ZipFile(files, 'w') as zf:
                for file in local_files:
                    zf.write(file, os.path.basename(file))
            files.seek(0)
            return send_file(files, as_attachment=True, attachment_filename='achieve.zip')
        else:
            files = local_files[0]
            return send_file(files, as_attachment=True)

    @app.route('/d/', methods=['POST'])
    def download_single():
        if request.method != 'POST':
            return

        file = request.form.get('filepath')

        print(request.form)
        return send_file(file, as_attachment=True)

    ip = get_devices()
    # print(f'\n\n\n\n{ip}\n\n\n\n')
    if ip:
        app.run(ip)
    else:
        app.run()


# def fldask_Server(files):

#     from flask import Flask, render_template, send_file

#     app = Flask(__name__)

#     @app.route('/')
#     def download_file():
#         if request.method != 'POST':
#             return
#         file = request.form.get('f')
#         return send_file(file, as_attachment=True)


def get_devices():

  
    try:
        # The following line creates a socket, connects to a remote server, and then gets the local IP address
        # that was used by the kernel to make that connection. It does not actually send any data to the remote server.
        local_ip = [(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]
    except Exception:
        local_ip = '127.0.0.1'
    return local_ip

print(get_local_ip())



def kill_server():
    sys.exit()


server_thread = threading.Thread(target=flask_Server, args=('l'))

if __name__ == '__main__':
    flask_Server('/home/famira/Music/kivyCalculator.mp4')
# print(get_devices())
