import os
from cryptography.fernet import Fernet
from threading import Lock


class Singleton(type):
    _instance = None
    _lock: Lock = Lock()
    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(Singleton, cls).__call__(*args, **kwargs)
            return cls._instance


class CryptoKey(metaclass=Singleton):
    """Singleton class which main role is to generate key (symmetric encryption) for conf.yaml"""
    def __init__(self):
        """
        PARAMETERS:
                key: bytes
                crypt: class Fernet
        """
        self.key = b'xyhn4el-90M7EqwQLjhb283uGaDrguQTBit9LWEqux8='
        self.crypto = Fernet(key=self.key)

    def get_encryption(self, string) -> bytes:
        bytes_ = bytes(string, 'utf-8')
        token = self.crypto.encrypt(bytes_)
        return token

    def get_decryption_string(self, bytes_) -> str:
        string = self.crypto.decrypt(bytes_).decode('utf-8')
        return string

#ob = CryptoKey()
#print(ob.get_encryption('postgres'))

# with open(os.getcwd() + '\\conf\\config.yaml') as f:
#     file = f.read()
#     encrypted = ob.get_encryption(file)
#     print(encrypted)
#     print(ob.get_decryption_string(encrypted))