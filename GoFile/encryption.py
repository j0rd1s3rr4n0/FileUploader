import os
from pathlib import Path

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class Encryption:
    MAGIC = b"FUENC1"
    SALT_SIZE = 16
    NONCE_SIZE = 12
    KEY_SIZE = 32
    ITERATIONS = 390000

    @staticmethod
    def _derive_key(password, salt):
        if not password:
            raise ValueError("Password is required for encryption and decryption")

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=Encryption.KEY_SIZE,
            salt=salt,
            iterations=Encryption.ITERATIONS,
        )
        return kdf.derive(password.encode("utf-8"))

    @staticmethod
    def encrypt_bytes(data, password):
        salt = os.urandom(Encryption.SALT_SIZE)
        nonce = os.urandom(Encryption.NONCE_SIZE)
        key = Encryption._derive_key(password, salt)
        ciphertext = AESGCM(key).encrypt(nonce, data, None)
        return Encryption.MAGIC + salt + nonce + ciphertext

    @staticmethod
    def decrypt_bytes(data, password):
        header_size = len(Encryption.MAGIC) + Encryption.SALT_SIZE + Encryption.NONCE_SIZE
        if len(data) <= header_size or not data.startswith(Encryption.MAGIC):
            raise ValueError("Invalid encrypted file format")

        offset = len(Encryption.MAGIC)
        salt = data[offset : offset + Encryption.SALT_SIZE]
        offset += Encryption.SALT_SIZE
        nonce = data[offset : offset + Encryption.NONCE_SIZE]
        ciphertext = data[offset + Encryption.NONCE_SIZE :]

        key = Encryption._derive_key(password, salt)
        return AESGCM(key).decrypt(nonce, ciphertext, None)

    @staticmethod
    def encrypt_file(filepath, password, output_path=None):
        source = Path(filepath)
        if not source.is_file():
            raise FileNotFoundError(f"File not found: {filepath}")

        target = Path(output_path) if output_path else source.with_name(source.name + ".enc")
        target.write_bytes(Encryption.encrypt_bytes(source.read_bytes(), password))
        return str(target)

    @staticmethod
    def decrypt_file(filepath, password, output_path=None):
        source = Path(filepath)
        if not source.is_file():
            raise FileNotFoundError(f"File not found: {filepath}")

        if output_path:
            target = Path(output_path)
        elif source.suffix == ".enc":
            target = source.with_suffix("")
        else:
            target = source.with_name(source.name + ".dec")

        target.write_bytes(Encryption.decrypt_bytes(source.read_bytes(), password))
        return str(target)
