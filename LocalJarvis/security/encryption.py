# Exemplo de criptografia (skeleton)
from cryptography.fernet import Fernet

def generate_key():
    return Fernet.generate_key()

def encrypt(data, key):
    f = Fernet(key)
    return f.encrypt(data.encode())

def decrypt(token, key):
    f = Fernet(key)
    return f.decrypt(token).decode()
