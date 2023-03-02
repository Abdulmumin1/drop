import json
import qrcode
scroll_var = """QScrollBar::vertical{width:6px;}
        QScrollBar::handle:vertical{background:#333; min-height:0px;}
        QScrollBar::handle:vertical:active{background:gray; border-radius:5px;}
        QScrollBar::add-line:vertical{height:0px;}
        QScrollBar::sub-line:vertical{height:0px;}
        """
scroll_hor = """QScrollBar::horizontal{height:6px;}
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


def generateQRCode():
    name = 'qr.png'
    qr = qrcode.QRCode(version=2,
                       box_size=5,
                       border=1)
    # Adding the data to be encoded to the QRCode object
    qr.add_data('http://192.168.43.14:5000/')
    qr.make(fit=True)  # Making the entire QR Code space utilized
    qr_image = qr.make_image()
    qr_image.save(name)
