import socket
import threading
import json
import random
import concurrent.futures
import os
from utils import load_data


def scan_network():
    ip_list = []
    subnet = '.'.join('192.168.43.14'.split('.')[:3])
    with concurrent.futures.ThreadPoolExecutor(max_workers=255) as executor:
        futures = [executor.submit(
            os.system, f'ping -n 1 {subnet}.{i}') for i in range(1, 255)]
        for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
            if future.result() == 0:
                ip_list.append(f'{subnet}.{i}')
    return ip_list


ip = socket.gethostbyname(socket.gethostname())
port = 5554


def handle():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((ip, port))
    data = load_data()
    data = json.dumps(data)

    def recieve_file():
        file_name = client.recv(1024).decode('ascii')
        print(file_name)
        _file = open(file_name, 'wb')

        # size of all buffer recieved

        while True:
            buffer = client.recv(5120)

            if not buffer:
                print(f'Finished recieving {file_name}.')
                client.close()
                break

            _file.write(buffer)
    while True:
        rec = client.recv(1024).decode()
        if rec == 'DATA':
            client.send(data.encode())
        elif rec == 'FILE':
            recieve_file()
        else:
            print(rec)
        print('running')


thread = threading.Thread(target=handle)

# def send_progress(total_size):
#     client.send(bytes(total_size))


# recieve_file(file_name_recv)
if __name__ == '__main__':
    print(scan_network())
