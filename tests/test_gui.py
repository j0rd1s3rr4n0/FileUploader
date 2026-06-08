import unittest

from fileuploader.models import ProviderError
from fileuploader_gui import GuiState, build_options, default_state, validate_state


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
        options = build_options(GuiState(api_key="key", api_key_env="KEY_ENV", url="https://example.test"))

        self.assertEqual(options["api_key"], "key")
        self.assertEqual(options["api_key_env"], "KEY_ENV")
        self.assertEqual(options["url"], "https://example.test")

    def test_validate_state_requires_upload_file(self):
        with self.assertRaises(ProviderError) as error:
            validate_state(GuiState(action="upload", path=""))

        self.assertEqual(error.exception.code, "path_required")


if __name__ == "__main__":
    unittest.main()
