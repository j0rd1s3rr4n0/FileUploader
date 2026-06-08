import importlib.util
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "GoFile" / "encryption.py"
SPEC = importlib.util.spec_from_file_location("gofile_encryption", MODULE_PATH)
gofile_encryption = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gofile_encryption)
Encryption = gofile_encryption.Encryption


class GoFileEncryptionTests(unittest.TestCase):
    def test_encrypt_decrypt_bytes_roundtrip(self):
        plaintext = b"private upload content"
        encrypted = Encryption.encrypt_bytes(plaintext, "correct horse battery staple")

        self.assertNotEqual(encrypted, plaintext)
        self.assertTrue(encrypted.startswith(Encryption.MAGIC))
        self.assertEqual(Encryption.decrypt_bytes(encrypted, "correct horse battery staple"), plaintext)

    def test_empty_password_is_rejected(self):
        with self.assertRaises(ValueError):
            Encryption.encrypt_bytes(b"payload", "")

    def test_decrypt_rejects_invalid_format(self):
        with self.assertRaises(ValueError):
            Encryption.decrypt_bytes(b"not-encrypted", "password")

    def test_encrypt_decrypt_file_roundtrip(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            source = workspace / "sample.txt"
            encrypted = workspace / "sample.txt.enc"
            decrypted = workspace / "sample.dec.txt"
            source.write_bytes(b"file payload")

            encrypted_path = Encryption.encrypt_file(source, "password", encrypted)
            decrypted_path = Encryption.decrypt_file(encrypted_path, "password", decrypted)

            self.assertEqual(Path(decrypted_path).read_bytes(), b"file payload")
            self.assertNotEqual(Path(encrypted_path).read_bytes(), b"file payload")


if __name__ == "__main__":
    unittest.main()
