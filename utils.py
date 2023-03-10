import json
import qrcode
import os
# from flask_server import get_devices
scroll_var = """QScrollBar::vertical{width:0px;}
        QScrollBar::handle:vertical{background:#333; min-height:0px;}
        QScrollBar::handle:vertical:active{background:gray; border-radius:5px;}
        QScrollBar::add-line:vertical{height:0px;}
        QScrollBar::sub-line:vertical{height:0px;}
        """
scroll_hor = """QScrollBar::horizontal{height:0px;}
        QScrollBar::handle:horizontal{background:#333; min-height:0px;}
        QScrollBar::handle:horizontal:active{background:gray; border-radius:5px;}
        QScrollBar::add-line:horizontal{height:0px;}
        QScrollBar::sub-line:horizontal{height:0px;}
        """


def save_data(name, color):
    json.dump({'name': name, 'color': color}, open('.config.json', 'w'))


def load_data():
    try:
        data = json.load(open('.config.json', 'r'))
    except:
        return
    return data


def create_download_files(files: list):
    json.dump({'files': files}, open('.send.json', 'w'))


def read_download_files():
    files = json.load(open('.send.json', 'r'))
    file_list = files['files']
    basename = list(map(lambda x: os.path.basename(x), file_list))
    return_list = list(zip(file_list, basename))
    return return_list


def retrieve_files():
    files = json.load(open('.send.json', 'r'))
    file_list = files['files']
    return file_list


def empty_download_files():
    json.dump({'files': []}, open('.send.json', 'w'))


def generateQRCode(get_devices):
    name = 'qr.png'
    qr = qrcode.QRCode(version=2,
                       box_size=5,
                       border=2)
    # Adding the data to be encoded to the QRCode object
    qr.add_data(f'http://{get_devices}:5000/')
    qr.make(fit=True)  # Making the entire QR Code space utilized
    qr_image = qr.make_image()
    qr_image.save(name)


def return_file_basename(file_names):
    names = list(map(lambda x: os.path.basename(x), file_names))
    return names
# create_download_files(['/home/famira/Videos/why her/Why.Her.E02.(NKIRI.COM).cytcytctrxerxtuyviujk.mkv', '/home/famira/Videos/why her/Why.Her.E03.(NKIRI.COM).nvfdoinbofnonoigfnbgf.mkv',
    #   '/home/famira/Videos/why her/Why.Her.E04.(NKIRI.COM).oivdfoinboingfbniogfibbg.mkv', '/home/famira/Videos/why her/Why.Her.E05.(NKIRI.COM).niovnfdoinbfognboifgbnh.mkv', '/home/famira/Videos/why her/Why.Her.E06.(NKIRI.COM).nionfvoidnoibonbgfoinfgbifbg.mkv'])
