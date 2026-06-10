import unittest

from fileuploader.models import ProviderError, ProviderInfo, UploadResult
from fileuploader_tui import FileUploaderTui, TuiRequest, request_options, service_table, validate_request


class FakeCore:
    def services(self, include_deprecated=True):
        return [ProviderInfo(name="gofile", display_name="GoFile")]

    def upload(self, service, path, **options):
        return UploadResult(provider=service, status=True, url="https://example.test", file_id="file-1")


class TuiSmokeTests(unittest.TestCase):
    def test_request_options_converts_empty_strings(self):
        options = request_options(TuiRequest(service="gofile", action="upload"))

        self.assertIsNone(options["api_key"])
        self.assertIsNone(options["api_key_env"])
        self.assertIsNone(options["url"])
        self.assertIsNone(options["password"])
        self.assertIsNone(options["ttl"])
        self.assertIsNone(options["max_downloads"])
        self.assertIsNone(options["notify_jid"])

    def test_request_options_keeps_provider_specific_values(self):
        options = request_options(
            TuiRequest(
                service="exploitsend",
                action="upload",
                password="secret",
                ttl="3600",
                max_downloads="3",
                notify_jid="user@example",
            )
        )

        self.assertEqual(options["password"], "secret")
        self.assertEqual(options["ttl"], "3600")
        self.assertEqual(options["max_downloads"], "3")
        self.assertEqual(options["notify_jid"], "user@example")

    def test_service_table_contains_provider_rows(self):
        table = service_table(FakeCore())

        self.assertEqual(len(table.rows), 1)

    def test_run_once_returns_normalized_result(self):
        tui = FileUploaderTui(core=FakeCore())
        result = tui.run_once(TuiRequest(service="gofile", action="upload", path="sample.txt"))

        self.assertTrue(result["ok"])
        self.assertEqual(result["result"]["provider"], "gofile")

    def test_validate_request_requires_upload_path(self):
        with self.assertRaises(ProviderError) as error:
            validate_request(TuiRequest(service="gofile", action="upload"))

        self.assertEqual(error.exception.code, "path_required")


if __name__ == "__main__":
    unittest.main()
