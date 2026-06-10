import json
import tempfile
import unittest
from pathlib import Path

from fileuploader import FileUploaderCore, ProviderError, create_default_registry
from fileuploader.providers import (
    FourSharedProvider,
    AnonFilesNewProvider,
    BlipbinProvider,
    BoxProvider,
    CatboxProvider,
    CuploadProvider,
    DropFileDevProvider,
    DropboxProvider,
    EasySendProvider,
    ExploitSendProvider,
    FileIoProvider,
    GoFileProvider,
    LitterboxProvider,
    MediaFireProvider,
    MegaProvider,
    MoonPushProvider,
    QurlProvider,
    TempShProvider,
    TmpFileLinkProvider,
    TransferShProvider,
    UguuProvider,
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
                "4shared",
                "anonfiles",
                "anonfilesnew",
                "bayfiles",
                "blipbin",
                "box",
                "catbox",
                "cupload",
                "dropfiledev",
                "dropbox",
                "easysend",
                "exploitsend",
                "fileio",
                "gofile",
                "jsonbin",
                "litterbox",
                "mediafire",
                "mega",
                "moonpush",
                "qurl",
                "tempsh",
                "tmpfilelink",
                "transfersh",
                "uguu",
            },
            names,
        )
        self.assertTrue(any(service.deprecated for service in services if service.name == "anonfiles"))
        self.assertTrue(any(service.deprecated for service in services if service.name == "bayfiles"))
        self.assertFalse(next(service.active for service in services if service.name == "mega"))

    def test_registry_active_only_excludes_deprecated_and_disabled_services(self):
        services = FileUploaderCore(create_default_registry()).services(include_deprecated=False)
        names = {service.name for service in services}

        self.assertNotIn("anonfiles", names)
        self.assertNotIn("bayfiles", names)
        self.assertNotIn("mega", names)
        self.assertIn("box", names)
        self.assertIn("dropbox", names)
        self.assertIn("fileio", names)
        self.assertIn("catbox", names)
        self.assertIn("4shared", names)
        self.assertIn("exploitsend", names)

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
            (TransferShProvider, "transfersh", "https://transfer.sh/sample.txt/abc"),
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

    def test_fileio_upload_normalizes_link_and_key(self):
        payload = {"success": True, "key": "abc123", "link": "https://file.io/abc123", "expiry": "14 days"}
        provider = FileIoProvider(http_client=FakeHttp(payload))

        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "sample.txt"
            source.write_text("data", encoding="utf-8")
            result = provider.upload(source)

        self.assertEqual(result.provider, "fileio")
        self.assertEqual(result.url, "https://file.io/abc123")
        self.assertEqual(result.file_id, "abc123")

    def test_uguu_upload_normalizes_first_file(self):
        payload = {
            "success": True,
            "files": [
                {
                    "hash": "hash-1",
                    "name": "sample.txt",
                    "url": "https://files.catbox.moe/sample.txt",
                    "size": 4,
                }
            ],
        }
        http = FakeHttp(payload)
        provider = UguuProvider(http_client=http)

        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "sample.txt"
            source.write_text("data", encoding="utf-8")
            result = provider.upload(source)

        self.assertEqual(result.provider, "uguu")
        self.assertEqual(result.url, "https://files.catbox.moe/sample.txt")
        self.assertEqual(result.file_id, "hash-1")
        self.assertIn("files[]", http.calls[0][2]["files"])

    def test_catbox_upload_uses_reqtype_and_file_field(self):
        http = FakeHttp(text="https://files.catbox.moe/sample.txt")
        provider = CatboxProvider(http_client=http)

        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "sample.txt"
            source.write_text("data", encoding="utf-8")
            result = provider.upload(source)

        self.assertEqual(result.provider, "catbox")
        self.assertEqual(result.url, "https://files.catbox.moe/sample.txt")
        self.assertEqual(http.calls[0][2]["data"]["reqtype"], "fileupload")
        self.assertIn("fileToUpload", http.calls[0][2]["files"])

    def test_litterbox_upload_uses_default_ttl(self):
        http = FakeHttp(text="https://litter.catbox.moe/sample.txt")
        provider = LitterboxProvider(http_client=http)

        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "sample.txt"
            source.write_text("data", encoding="utf-8")
            result = provider.upload(source)

        self.assertEqual(result.provider, "litterbox")
        self.assertEqual(result.url, "https://litter.catbox.moe/sample.txt")
        self.assertEqual(result.metadata["ttl"], "1h")
        self.assertEqual(http.calls[0][2]["data"]["time"], "1h")

    def test_box_upload_uses_oauth_token_and_root_folder(self):
        payload = {
            "entries": [
                {
                    "id": "box-file-1",
                    "name": "sample.txt",
                    "shared_link": {"url": "https://box.com/s/file"},
                }
            ]
        }
        http = FakeHttp(payload)
        provider = BoxProvider(http_client=http)

        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "sample.txt"
            source.write_text("data", encoding="utf-8")
            result = provider.upload(source, api_key="box-token")

        self.assertEqual(result.provider, "box")
        self.assertEqual(result.url, "https://box.com/s/file")
        self.assertEqual(result.file_id, "box-file-1")
        self.assertEqual(http.calls[0][2]["headers"]["Authorization"], "Bearer box-token")

    def test_4shared_upload_uses_oauth_params_and_folder(self):
        payload = {
            "id": "four-file-1",
            "name": "sample.txt",
            "downloadPage": "https://www.4shared.com/file/four-file-1/sample.html",
        }
        http = FakeHttp(payload)
        provider = FourSharedProvider(http_client=http)

        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "sample.txt"
            source.write_text("data", encoding="utf-8")
            result = provider.upload(source, api_key="?oauth_token=tok&oauth_signature=sig", folder_id="folder-1")

        self.assertEqual(result.provider, "4shared")
        self.assertEqual(result.url, "https://www.4shared.com/file/four-file-1/sample.html")
        self.assertEqual(result.file_id, "four-file-1")
        self.assertEqual(http.calls[0][1], "https://upload.4shared.com/v1_2/files?oauth_token=tok&oauth_signature=sig")
        self.assertEqual(http.calls[0][2]["params"]["folderId"], "folder-1")
        self.assertEqual(http.calls[0][2]["params"]["fileName"], "sample.txt")
        self.assertEqual(http.calls[0][2]["headers"]["Content-Type"], "application/octet-stream")

    def test_4shared_info_uses_oauth_params(self):
        payload = {"id": "four-file-1", "name": "sample.txt"}
        http = FakeHttp(payload)
        provider = FourSharedProvider(http_client=http)

        result = provider.info_file("four-file-1", api_key="oauth_token=tok")

        self.assertEqual(result["id"], "four-file-1")
        self.assertEqual(http.calls[0][1], "https://api.4shared.com/v1_2/files/four-file-1?oauth_token=tok")

    def test_exploit_send_upload_encrypts_and_normalizes_url(self):
        payload = {"success": True, "id": "send-file-1"}
        http = FakeHttp(payload)
        provider = ExploitSendProvider(http_client=http)

        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "sample.txt"
            source.write_text("data", encoding="utf-8")
            result = provider.upload(source, password="secret", ttl="3600", max_downloads="5")

        self.assertEqual(result.provider, "exploitsend")
        self.assertTrue(result.url.startswith("https://send.exploit.in/#send-file-1!"))
        self.assertEqual(result.file_id, "send-file-1")
        self.assertEqual(http.calls[0][1], "https://send.exploit.in/api/upload")
        self.assertEqual(http.calls[0][2]["data"]["filename"], "sample.txt")
        self.assertEqual(http.calls[0][2]["data"]["ttl"], "3600")
        self.assertEqual(http.calls[0][2]["data"]["max_downloads"], "5")
        encrypted_file = http.calls[0][2]["files"]["file"]
        encrypted_bytes = encrypted_file[1]
        self.assertEqual(encrypted_file[0], "encrypted.bin")
        self.assertGreater(len(encrypted_bytes), len("data"))
        self.assertEqual(int.from_bytes(encrypted_bytes[:4], "big"), 12)

    def test_exploit_send_info_uses_check_endpoint(self):
        payload = {"exists": True, "available": True, "filename": "sample.txt"}
        http = FakeHttp(payload)
        provider = ExploitSendProvider(http_client=http)

        result = provider.info_file("send-file-1")

        self.assertTrue(result["exists"])
        self.assertEqual(http.calls[0][1], "https://send.exploit.in/api/check")
        self.assertEqual(http.calls[0][2]["params"]["id"], "send-file-1")

    def test_dropbox_upload_uses_content_endpoint(self):
        payload = {"id": "dropbox-file-1", "path_display": "/sample.txt", "name": "sample.txt"}
        http = FakeHttp(payload)
        provider = DropboxProvider(http_client=http)

        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "sample.txt"
            source.write_text("data", encoding="utf-8")
            result = provider.upload(source, api_key="dropbox-token")

        self.assertEqual(result.provider, "dropbox")
        self.assertEqual(result.url, "/sample.txt")
        self.assertEqual(result.file_id, "dropbox-file-1")
        self.assertEqual(http.calls[0][1], "https://content.dropboxapi.com/2/files/upload")
        self.assertEqual(http.calls[0][2]["headers"]["Authorization"], "Bearer dropbox-token")

    def test_mediafire_upload_uses_session_token(self):
        payload = {
            "response": {
                "doupload": {
                    "quickkey": "mf-file-1",
                    "normal_download": "https://www.mediafire.com/file/mf-file-1/sample.txt",
                }
            }
        }
        http = FakeHttp(payload)
        provider = MediaFireProvider(http_client=http)

        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "sample.txt"
            source.write_text("data", encoding="utf-8")
            result = provider.upload(source, api_key="mediafire-session")

        self.assertEqual(result.provider, "mediafire")
        self.assertEqual(result.url, "https://www.mediafire.com/file/mf-file-1/sample.txt")
        self.assertEqual(result.file_id, "mf-file-1")
        self.assertEqual(http.calls[0][2]["params"]["session_token"], "mediafire-session")

    def test_account_provider_requires_token(self):
        provider = DropboxProvider(http_client=FakeHttp({}))

        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "sample.txt"
            source.write_text("data", encoding="utf-8")
            with self.assertRaises(ProviderError) as error:
                provider.upload(source)

        self.assertEqual(error.exception.code, "api_key_required")

    def test_mega_provider_is_disabled(self):
        provider = MegaProvider()

        with self.assertRaises(ProviderError) as error:
            provider.upload("sample.txt")

        self.assertEqual(error.exception.code, "provider_disabled")


if __name__ == "__main__":
    unittest.main()
