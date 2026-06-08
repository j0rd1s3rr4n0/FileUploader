import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "JSONBin.com" / "jsonbin_uploader.py"
SPEC = importlib.util.spec_from_file_location("jsonbin_uploader", MODULE_PATH)
jsonbin_uploader = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(jsonbin_uploader)


class JsonBinUploaderTests(unittest.TestCase):
    def test_parse_size_accepts_bytes_and_binary_units(self):
        cases = {
            "42": 42,
            "42b": 42,
            "1KB": 1024,
            "1.5mb": 1572864,
        }

        for value, expected in cases.items():
            with self.subTest(value=value):
                self.assertEqual(jsonbin_uploader.parse_size(value), expected)

    def test_parse_api_keys_combines_arguments_and_environment(self):
        original_value = os.environ.get(jsonbin_uploader.API_KEYS_ENV)
        os.environ[jsonbin_uploader.API_KEYS_ENV] = "env-key-1, env-key-2"
        try:
            self.assertEqual(
                jsonbin_uploader.parse_api_keys(["arg-key-1,arg-key-2", "arg-key-3"]),
                ["arg-key-1", "arg-key-2", "arg-key-3", "env-key-1", "env-key-2"],
            )
        finally:
            if original_value is None:
                os.environ.pop(jsonbin_uploader.API_KEYS_ENV, None)
            else:
                os.environ[jsonbin_uploader.API_KEYS_ENV] = original_value

    def test_build_chunk_record_contains_verifiable_metadata(self):
        file_path = Path("sample.txt")
        chunk_data = b"hello"
        file_hash = jsonbin_uploader.sha256_bytes(chunk_data)

        record = jsonbin_uploader.build_chunk_record(
            "upload-1",
            file_path,
            file_hash,
            total_parts=1,
            chunk_index=0,
            chunk_data=chunk_data,
        )

        self.assertEqual(record["upload_id"], "upload-1")
        self.assertEqual(record["original_filename"], "sample.txt")
        self.assertEqual(record["chunk_size"], 5)
        self.assertEqual(record["chunk_sha256"], file_hash)
        self.assertEqual(record["file_sha256"], file_hash)
        self.assertEqual(record["content_encoding"], "base64")
        self.assertEqual(record["content"], "aGVsbG8=")

    def test_reconstruct_manifest_writes_and_verifies_output(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            parts_dir = workspace / "parts"
            parts_dir.mkdir()
            expected_content = b"hello world"
            (parts_dir / "0.part").write_bytes(expected_content[:6])
            (parts_dir / "1.part").write_bytes(expected_content[6:])

            manifest = {
                "original_filename": "sample.txt",
                "total_parts": 2,
                "file_sha256": jsonbin_uploader.sha256_bytes(expected_content),
            }
            manifest_file = workspace / "manifest.json"
            manifest_file.write_text(json.dumps(manifest), encoding="utf-8")
            output_file = workspace / "output.txt"

            args = type(
                "Args",
                (),
                {
                    "manifest_file": str(manifest_file),
                    "parts_dir": str(parts_dir),
                    "output": str(output_file),
                },
            )

            result = jsonbin_uploader.reconstruct_from_manifest(args)

            self.assertEqual(output_file.read_bytes(), expected_content)
            self.assertTrue(result["verified"])


if __name__ == "__main__":
    unittest.main()
