import json
import tempfile
import unittest
from pathlib import Path

from fileuploader import FileUploaderCore, ProviderError, create_default_registry
from fileuploader.providers import (
    AnonFilesNewProvider,
    BlipbinProvider,
    CuploadProvider,
    DropFileDevProvider,
    EasySendProvider,
    GoFileProvider,
    MoonPushProvider,
    QurlProvider,
    TempShProvider,
    TmpFileLinkProvider,
    ZeroXZeroProvider,
)


class FakeResponse:
    def __init__(self, payload, status_code=200, text=None, headers=None):
        self.payload = payload
        self.status_code = status_code
        self.text = text if text is not None else json.dumps(payload)
        self.headers = headers or {}

    def json(self):
        if isinstance(self.payload, Exception):
            raise self.payload
        return self.payload


class FakeHttp:
    def __init__(self, payload=None, text=None, headers=None):
        self.payload = payload
        self.text = text
        self.headers = headers
        self.calls = []

    def post(self, url, **kwargs):
        self.calls.append(("post", url, kwargs))
        return FakeResponse(self.payload, text=self.text, headers=self.headers)

    def put(self, url, **kwargs):
        self.calls.append(("put", url, kwargs))
        return FakeResponse(self.payload, text=self.text, headers=self.headers)

    def get(self, url, **kwargs):
        self.calls.append(("get", url, kwargs))
        return FakeResponse(self.payload, text=self.text, headers=self.headers)


class ProviderCoreTests(unittest.TestCase):
    def test_registry_lists_active_and_deprecated_services(self):
        services = FileUploaderCore(create_default_registry()).services()
        names = {service.name for service in services}

        self.assertEqual(
            {
                "0x0",
                "anonfiles",
                "anonfilesnew",
                "bayfiles",
                "blipbin",
                "cupload",
                "dropfiledev",
                "easysend",
                "gofile",
                "jsonbin",
                "moonpush",
                "qurl",
                "tempsh",
                "tmpfilelink",
            },
            names,
        )
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
                "id": "file-1",
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

    def test_plain_text_multipart_providers_normalize_urls(self):
        providers = [
            (ZeroXZeroProvider, "https://0x0.st/abc.txt"),
            (TempShProvider, "https://temp.sh/abc/sample.txt"),
        ]

        for provider_class, expected_url in providers:
            with self.subTest(provider=provider_class.__name__):
                provider = provider_class(http_client=FakeHttp(text=f"{expected_url}\n"))
                with tempfile.TemporaryDirectory() as temp_dir:
                    source = Path(temp_dir) / "sample.txt"
                    source.write_text("data", encoding="utf-8")
                    result = provider.upload(source)

                self.assertEqual(result.url, expected_url)
                self.assertTrue(result.status)

    def test_moonpush_upload_normalizes_json_urls(self):
        payload = {
            "shareUrl": "https://www.moonpush.com/share/abc#key",
            "downloadUrl": "https://www.moonpush.com/api/dl/abc",
            "pipeId": "abc",
        }
        provider = MoonPushProvider(http_client=FakeHttp(payload))

        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "sample.txt"
            source.write_text("data", encoding="utf-8")
            result = provider.upload(source)

        self.assertEqual(result.url, "https://www.moonpush.com/share/abc#key")
        self.assertEqual(result.short_url, "https://www.moonpush.com/api/dl/abc")
        self.assertEqual(result.file_id, "abc")

    def test_tmpfilelink_upload_normalizes_download_link(self):
        payload = {
            "fileName": "sample.txt",
            "downloadLink": "https://d.tmpfile.link/sample.txt",
            "downloadLinkEncoded": "https://tmpfile.link/qr/sample",
        }
        provider = TmpFileLinkProvider(http_client=FakeHttp(payload))

        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "sample.txt"
            source.write_text("data", encoding="utf-8")
            result = provider.upload(source)

        self.assertEqual(result.url, "https://d.tmpfile.link/sample.txt")
        self.assertEqual(result.short_url, "https://tmpfile.link/qr/sample")

    def test_blipbin_upload_preserves_delete_token(self):
        provider = BlipbinProvider(http_client=FakeHttp(text="https://blipbin.com/a3Bx9k", headers={"X-Token": "delete-me"}))

        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "sample.txt"
            source.write_text("data", encoding="utf-8")
            result = provider.upload(source)

        self.assertEqual(result.url, "https://blipbin.com/a3Bx9k")
        self.assertEqual(result.metadata["delete_token"], "delete-me")

    def test_easysend_upload_expands_relative_share_url(self):
        provider = EasySendProvider(http_client=FakeHttp({"share_url": "/Ab3Kz", "short_code": "Ab3Kz"}))

        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "sample.txt"
            source.write_text("data", encoding="utf-8")
            result = provider.upload(source)

        self.assertEqual(result.url, "https://easysend.co/Ab3Kz")
        self.assertEqual(result.file_id, "Ab3Kz")

    def test_put_upload_providers_normalize_urls(self):
        providers = [
            (DropFileDevProvider, "dropfiledev", "https://dropfile.dev/f/sample.txt"),
            (CuploadProvider, "cupload", "https://cupload.io/f/sample.txt"),
            (QurlProvider, "qurl", "https://qurl.sh/f/sample.txt"),
        ]

        for provider_class, provider_name, expected_url in providers:
            with self.subTest(provider=provider_name):
                http = FakeHttp(text=expected_url)
                provider = provider_class(http_client=http)
                with tempfile.TemporaryDirectory() as temp_dir:
                    source = Path(temp_dir) / "sample.txt"
                    source.write_text("data", encoding="utf-8")
                    result = provider.upload(source)

                self.assertEqual(result.provider, provider_name)
                self.assertEqual(result.url, expected_url)
                self.assertEqual(http.calls[0][0], "put")
                self.assertTrue(http.calls[0][1].endswith("/sample.txt"))


if __name__ == "__main__":
    unittest.main()
