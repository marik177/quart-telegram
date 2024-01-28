from qrcode import QRCode
from PIL import Image
from io import BytesIO
import base64


class QRCodeBot(QRCode):
    """
    A simple QR code generator bot based on the QRCode library.
    """

    def generate_qr(self, token: str):
        """
        Generates a QR code for the given token.
        :param token: The data to encode in the QR code.
        """
        self.clear()
        self.add_data(token)
        img = self.make_image(fill_color="black", back_color="white")
        return img

    def display_url_as_qr(self, url):
        """
        Displays a QR code for the given URL.
        :param url: The URL to encode in the QR code.
        """
        img = self.generate_qr(url)
        img.show()
        return img

