from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import padding as sym_padding

class Encryption:
    @staticmethod
    def _pad(data):
        padder = sym_padding.PKCS7(128).padder()
        padded_data = padder.update(data)
        padded_data += padder.finalize()
        return padded_data

    @staticmethod
    def _unpad(padded_data):
        unpadder = sym_padding.PKCS7(128).unpadder()
        data = unpadder.update(padded_data)
        data += unpadder.finalize()
        return data

    @staticmethod
    def _derive_key(password, salt=b''):
        backend = default_backend()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=backend
        )
        return kdf.derive(password.encode())

    @staticmethod
    def generate_rsa_key():
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        return private_key, public_key

    @staticmethod
    def serialize_key(key):
        return key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )

    @staticmethod
    def deserialize_key(serialized_key):
        return serialization.load_pem_private_key(
            serialized_key,
            password=None,
            backend=default_backend()
        )

    @staticmethod
    def encrypt_text(text, password, algorithm="AES"):
        if algorithm == "AES":
            iv = os.urandom(16)
            key = Encryption._derive_key(password)
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
            encryptor = cipher.encryptor()
            padded_data = Encryption._pad(text.encode())
            encrypted_text = encryptor.update(padded_data) + encryptor.finalize()
            return encrypted_text, iv
        elif algorithm == "RSA":
            private_key, _ = Encryption.generate_rsa_key()
            ciphertext = private_key.encrypt(
                text.encode(),
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            return ciphertext, None
        else:
            raise ValueError("Unknown encryption algorithm")

    @staticmethod
    def decrypt_text(encrypted_text, iv, password, algorithm="AES"):
        if algorithm == "AES":
            key = Encryption._derive_key(password)
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            decrypted_data = decryptor.update(encrypted_text) + decryptor.finalize()
            return Encryption._unpad(decrypted_data).decode()
        elif algorithm == "RSA":
            private_key, _ = Encryption.generate_rsa_key()
            decrypted_text = private_key.decrypt(
                encrypted_text,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            return decrypted_text.decode()
        else:
            raise ValueError("Unknown decryption algorithm")
