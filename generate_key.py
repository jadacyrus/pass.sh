import base64
import binascii
import os

print(base64.urlsafe_b64encode(binascii.hexlify(os.urandom(16))).decode())
