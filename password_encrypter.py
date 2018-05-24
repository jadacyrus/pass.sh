from cryptography.fernet import Fernet
import base64

class PasswordEncrypter:

    def __init__(self, key):
        self.transformer = Fernet(key.encode())
       
    def encrypt(self, plaintext):
        ciphertext = self.transformer.encrypt(plaintext.encode())
        return ciphertext.decode()

    def decrypt(self, ciphertext):
        plaintext = self.transformer.decrypt(ciphertext.encode())
        return plaintext.decode()
