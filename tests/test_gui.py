import unittest

from fileuploader.models import ProviderError, ProviderInfo
from fileuploader_gui import (
    GuiState,
    actions_for_service,
    active_services,
    build_options,
    default_service_name,
    default_state,
    deprecated_services,
    provider_status,
    provider_summary,
    required_fields_for_state,
    service_names,
    validate_state,
)


class GuiSmokeTests(unittest.TestCase):
    def test_default_state_is_upload_with_gofile(self):
        state = default_state()

        self.assertEqual(state.service, "gofile")
        self.assertEqual(state.action, "upload")

    def test_build_options_converts_empty_strings_to_none(self):
        options = build_options(GuiState(api_key="", api_key_env="", url=""))

        self.assertIsNone(options["api_key"])
        self.assertIsNone(options["api_key_env"])
        self.assertIsNone(options["url"])

    def test_build_options_keeps_user_values(self):
        options = build_options(
            GuiState(
                api_key="key",
                api_key_env="KEY_ENV",
                url="https://example.test",
                password="secret",
                ttl="3600",
                max_downloads="3",
                notify_jid="user@example",
            )
        )

        self.assertEqual(options["api_key"], "key")
        self.assertEqual(options["api_key_env"], "KEY_ENV")
        self.assertEqual(options["url"], "https://example.test")
        self.assertEqual(options["password"], "secret")
        self.assertEqual(options["ttl"], "3600")
        self.assertEqual(options["max_downloads"], "3")
        self.assertEqual(options["notify_jid"], "user@example")

    def test_validate_state_requires_upload_file(self):
        with self.assertRaises(ProviderError) as error:
            validate_state(GuiState(action="upload", path=""))

        self.assertEqual(error.exception.code, "path_required")

    def test_active_services_excludes_deprecated_and_disabled_services(self):
        services = [
            ProviderInfo(name="gofile", display_name="GoFile"),
            ProviderInfo(name="bayfiles", display_name="BayFiles", deprecated=True),
            ProviderInfo(name="mega", display_name="MEGA", active=False),
        ]

        self.assertEqual(service_names(active_services(services)), ["gofile"])
        self.assertEqual(service_names(deprecated_services(services)), ["bayfiles", "mega"])

    def test_provider_status_labels_state(self):
        self.assertEqual(provider_status(ProviderInfo(name="gofile", display_name="GoFile")), "active")
        self.assertEqual(provider_status(ProviderInfo(name="bayfiles", display_name="BayFiles", deprecated=True)), "deprecated")
        self.assertEqual(provider_status(ProviderInfo(name="mega", display_name="MEGA", active=False)), "disabled")

    def test_provider_summary_mentions_capabilities_and_credentials(self):
        summary = provider_summary(ProviderInfo(name="box", display_name="Box", supports_info=True, requires_api_key=True))

        self.assertIn("Box", summary)
        self.assertIn("upload", summary)
        self.assertIn("info", summary)
        self.assertIn("token required", summary)

    def test_default_service_prefers_gofile(self):
        services = [
            ProviderInfo(name="anonfilesnew", display_name="AnonFilesNew"),
            ProviderInfo(name="gofile", display_name="GoFile"),
        ]

        self.assertEqual(default_service_name(services), "gofile")

    def test_actions_follow_provider_capabilities(self):
        service = ProviderInfo(name="anonfilesnew", display_name="AnonFilesNew", supports_download=False, supports_info=True)

        self.assertEqual(actions_for_service(service), ["upload", "info"])

    def test_required_fields_follow_action_and_api_key(self):
        service = ProviderInfo(name="anonfilesnew", display_name="AnonFilesNew", supports_info=True, requires_api_key=True)

        fields = required_fields_for_state(GuiState(action="info"), service)

        self.assertEqual(fields, {"file_id", "api_key"})

    def test_required_fields_include_exploit_send_upload_options(self):
        service = ProviderInfo(name="exploitsend", display_name="Exploit.IN Send", supports_info=True)

        fields = required_fields_for_state(GuiState(service="exploitsend", action="upload"), service)

        self.assertEqual(fields, {"path", "password", "ttl", "max_downloads", "notify_jid"})

    def test_validate_state_rejects_unsupported_action(self):
        service = ProviderInfo(name="jsonbin", display_name="JSONBin", supports_download=False)

        with self.assertRaises(ProviderError) as error:
            validate_state(GuiState(service="jsonbin", action="download", url="https://example.test"), service)

        self.assertEqual(error.exception.code, "unsupported_action")

    def test_validate_state_requires_api_key_for_api_key_services(self):
        service = ProviderInfo(name="jsonbin", display_name="JSONBin", requires_api_key=True)

        with self.assertRaises(ProviderError) as error:
            validate_state(GuiState(service="jsonbin", action="upload", path="file.txt"), service)

        self.assertEqual(error.exception.code, "api_key_required")


if __name__ == "__main__":
    unittest.main()
