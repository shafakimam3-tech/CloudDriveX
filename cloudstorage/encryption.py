from cryptography.fernet import Fernet

def load_key():
    return open("secret.key", "rb").read()

key = load_key()
fernet = Fernet(key)

def encrypt_file(file_data):
    return fernet.encrypt(file_data)

def decrypt_file(file_data):
    return fernet.decrypt(file_data)