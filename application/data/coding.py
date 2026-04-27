import base64
import hmac
import hashlib
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


def generate_key_from_password(password: str, salt: bytes):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key


def encode_message(message: str, key: bytes) -> str:
    raw_key = base64.urlsafe_b64decode(key)
    iv = hmac.new(raw_key, message.encode(), hashlib.sha256).digest()[:16]
    cipher = Cipher(algorithms.AES(raw_key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(128).padder()
    padded = padder.update(message.encode()) + padder.finalize()
    ct = encryptor.update(padded) + encryptor.finalize()
    return base64.urlsafe_b64encode(iv + ct).decode()

def decode_message(encrypted_message: str, key: bytes) -> str:
    raw_key = base64.urlsafe_b64decode(key)
    data = base64.urlsafe_b64decode(encrypted_message.encode())
    iv, ct = data[:16], data[16:]
    cipher = Cipher(algorithms.AES(raw_key), modes.CBC(iv))
    decryptor = cipher.decryptor()
    padded = decryptor.update(ct) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    return (unpadder.update(padded) + unpadder.finalize()).decode()









if __name__ == "__main__":
    password = "my_secure_password"
    salt = b"this_is_a_complex_salt"
    key = generate_key_from_password(password, salt)
    message = "Привет! Это секретное сообщение."
    encrypted_message = encode_message(message, key)
    print(f"Encrypted message: {encrypted_message}")
    decrypted_message = decode_message(encrypted_message, key)
    print(f"Decrypted message: {decrypted_message}")
    print(f"Generated key: {key.decode()}")