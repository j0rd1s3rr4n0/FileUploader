import json
import subprocess
import sys
import unittest
from unittest.mock import patch

from typer.testing import CliRunner

from fileuploader.cli import app, build_guided_download, build_guided_info, build_guided_upload
from fileuploader.models import ProviderError, ProviderInfo, UploadResult


class FakeCore:
    def services(self, include_deprecated=True):
        return [
            ProviderInfo(name="gofile", display_name="GoFile"),
            ProviderInfo(name="bayfiles", display_name="BayFiles", deprecated=True),
        ]

    def upload(self, service, path, **options):
        if service == "missing":
            raise ProviderError(service, "Unknown provider")
        return UploadResult(provider=service, status=True, url="https://example.test/file", file_id="file-1")

    def download(self, service, **options):
        return {"provider": service, "download": options}

    def info(self, service, file_id, **options):
        return {"provider": service, "file_id": file_id}


class CliTests(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    @patch("fileuploader.cli.FileUploaderCore", return_value=FakeCore())
    def test_services_lists_all_providers_as_json(self, _core):
        result = self.runner.invoke(app, ["services", "--json"])

        self.assertEqual(result.exit_code, 0, result.output)
        payload = json.loads(result.output)
        self.assertEqual({"gofile", "bayfiles"}, {item["name"] for item in payload})

    @patch("fileuploader.cli.FileUploaderCore", return_value=FakeCore())
    def test_services_default_output_is_readable_table(self, _core):
        result = self.runner.invoke(app, ["services"])

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("Service", result.output)
        self.assertIn("gofile", result.output)
        self.assertIn("deprecated", result.output)

    @patch("fileuploader.cli.FileUploaderCore", return_value=FakeCore())
    def test_upload_outputs_json(self, _core):
        result = self.runner.invoke(app, ["upload", "sample.txt", "--service", "gofile", "--json"])

        self.assertEqual(result.exit_code, 0, result.output)
        payload = json.loads(result.output)
        self.assertEqual(payload["provider"], "gofile")
        self.assertEqual(payload["url"], "https://example.test/file")

    @patch("fileuploader.cli.FileUploaderCore", return_value=FakeCore())
    def test_upload_invalid_provider_returns_error(self, _core):
        result = self.runner.invoke(app, ["upload", "sample.txt", "--service", "missing", "--json"])

        self.assertEqual(result.exit_code, 1)
        payload = json.loads(result.output)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error"]["provider"], "missing")

    @patch("fileuploader.cli.FileUploaderCore", return_value=FakeCore())
    def test_guided_upload_flow(self, _core):
        result = self.runner.invoke(
            app,
            ["guided"],
            input="gofile\nupload\nn\nsample.txt\n\n\n",
        )

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("https://example.test/file", result.output)

    def test_guided_helpers_validate_missing_values(self):
        with self.assertRaises(ProviderError) as error:
            build_guided_upload(FakeCore(), "gofile", "", None, None)
        self.assertEqual(error.exception.code, "path_required")

        with self.assertRaises(ProviderError) as error:
            build_guided_download(FakeCore(), "gofile", "")
        self.assertEqual(error.exception.code, "url_required")

        with self.assertRaises(ProviderError) as error:
            build_guided_info(FakeCore(), "gofile", "", None, None)
        self.assertEqual(error.exception.code, "file_id_required")

    def test_standalone_cli_launcher_shows_services(self):
        result = subprocess.run(
            [sys.executable, "-m", "fileuploader_cli", "services", "--json"],
            check=True,
            capture_output=True,
            text=True,
        )

        payload = json.loads(result.stdout)
        self.assertTrue(any(item["name"] == "gofile" for item in payload))


if __name__ == "__main__":
    unittest.main()
