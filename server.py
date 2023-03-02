import socket
import threading
import os
import time
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def init_server():
    ip = socket.gethostbyname(socket.gethostname())
    port = 5554
    print(ip)

    server.bind((ip, port))
    server.listen()
    print(f'Server is listening on {ip}:{port}')


def send_to_client(client, file_path: str):
    file_name = os.path.basename(file_path)

    client.send(file_name.encode('ascii'))
    time.sleep(0.3)

    _file = open(file_path, 'rb')
    buffer = _file.read(1024)
    while buffer:
        client.send(buffer)
        buffer = _file.read(1024)


def send_multiple(client, files: list):
    for file in files:
        send_to_client(client, file)


def destroy_server():
    server.close()
