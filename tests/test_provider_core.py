import json
import tempfile
import unittest
from pathlib import Path

from fileuploader import FileUploaderCore, ProviderError, create_default_registry
from fileuploader.providers import AnonFilesNewProvider, GoFileProvider


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self.payload = payload
        self.status_code = status_code
        self.text = json.dumps(payload)

    def json(self):
        return self.payload


class FakeHttp:
    def __init__(self, payload):
        self.payload = payload
        self.calls = []

    def post(self, url, **kwargs):
        self.calls.append(("post", url, kwargs))
        return FakeResponse(self.payload)

    def get(self, url, **kwargs):
        self.calls.append(("get", url, kwargs))
        return FakeResponse(self.payload)


class ProviderCoreTests(unittest.TestCase):
    def test_registry_lists_active_and_deprecated_services(self):
        services = FileUploaderCore(create_default_registry()).services()
        names = {service.name for service in services}

        self.assertEqual({"anonfiles", "anonfilesnew", "bayfiles", "gofile", "jsonbin"}, names)
        self.assertTrue(any(service.deprecated for service in services if service.name == "anonfiles"))
        self.assertTrue(any(service.deprecated for service in services if service.name == "bayfiles"))

    def test_unknown_provider_raises_normalized_error(self):
        with self.assertRaises(ProviderError) as error:
            FileUploaderCore(create_default_registry()).upload("missing", "file.txt")

        self.assertEqual(error.exception.provider, "missing")
        self.assertIn("Unknown provider", error.exception.message)

    def test_provider_lookup_is_case_insensitive(self):
        provider = create_default_registry().get("GoFile")

        self.assertEqual(provider.info.name, "gofile")

    def test_gofile_upload_normalizes_result(self):
        payload = {
            "status": "ok",
            "data": {
                "downloadPage": "https://gofile.io/d/abc",
                "fileId": "file-1",
                "fileName": "sample.txt",
            },
        }
        provider = GoFileProvider(http_client=FakeHttp(payload))

        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "sample.txt"
            source.write_text("data", encoding="utf-8")
            result = provider.upload(source)

        self.assertTrue(result.status)
        self.assertEqual(result.provider, "gofile")
        self.assertEqual(result.url, "https://gofile.io/d/abc")
        self.assertEqual(result.file_id, "file-1")

    def test_anonfilesnew_upload_normalizes_result_and_api_key(self):
        payload = {
            "status": True,
            "data": {
                "file": {
                    "url": {"full": "https://anonfilesnew.com/full", "short": "https://anonfilesnew.com/s"},
                    "metadata": {"id": "file-1", "name": "sample.txt"},
                }
            },
        }
        http = FakeHttp(payload)
        provider = AnonFilesNewProvider(http_client=http)

        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "sample.txt"
            source.write_text("data", encoding="utf-8")
            result = provider.upload(source, api_key="secret")

        self.assertEqual(result.provider, "anonfilesnew")
        self.assertEqual(result.file_id, "file-1")
        self.assertEqual(result.short_url, "https://anonfilesnew.com/s")
        self.assertIn("?key=secret", http.calls[0][1])


if __name__ == "__main__":
    unittest.main()
