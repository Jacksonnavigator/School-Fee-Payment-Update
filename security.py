from cryptography.fernet import Fernet
import hashlib
import base64

class SecurityManager:
    def __init__(self, key):
        self.cipher = Fernet(key.encode())

    def encrypt_data(self, data):
        """Encrypt sensitive data"""
        return self.cipher.encrypt(data.encode()).decode()

    def decrypt_data(self, encrypted_data):
        """Decrypt sensitive data"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()

    def hash_password(self, password):
        """Hash passwords using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

# Generate a key for encryption if needed (run once and store in config)
# key = Fernet.generate_key()
# print(key.decode())