import qrcode
import os

def generate_qr(url):
    img = qrcode.make(url)

    path = os.path.join("static", "qr.png")
    img.save(path)

    return "qr.png"