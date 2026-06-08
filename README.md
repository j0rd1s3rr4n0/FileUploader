# FileUploader

Unified Python tooling for uploading files to multiple file-hosting providers.

[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-active-success.svg)](#supported-providers)

FileUploader provides a shared provider layer plus three user interfaces:

- **CLI** for automation and scripts: `python -m fileuploader`
- **GUI** for desktop users: `python -m fileuploader_gui`
- **TUI** for guided terminal use: `python -m fileuploader_tui`

The current provider set includes GoFile, AnonFilesNew, JSONBin, AnonFiles, and BayFiles. Deprecated providers remain available for compatibility, but upstream APIs may be unreliable.

## Features

| Feature | Description |
| --- | --- |
| Unified provider core | Normalized provider metadata, upload results, and errors across services. |
| Multiple interfaces | CLI, Tkinter GUI, and Rich TUI use the same core behavior. |
| API key support | Pass keys directly or through environment variables. |
| Encryption support | GoFile legacy workflow supports local AES-GCM encrypt/decrypt before and after transfer. |
| Clipboard support | Copy processed output from supported workflows. |
| Testable design | Provider and UI tests use mocks and avoid network access. |

## Installation

```shell
git clone https://github.com/j0rd1s3rr4n0/FileUploader.git
cd FileUploader
python -m pip install -r requirements.txt
```

## Quick Start

List all providers:

```shell
python -m fileuploader services
```

Upload a file with GoFile and print JSON:

```shell
python -m fileuploader upload --service gofile path/to/file.txt --json
```

Upload with AnonFilesNew using an API key:

```shell
python -m fileuploader upload --service anonfilesnew path/to/file.txt --api-key YOUR_API_KEY --json
```

Use an API key from an environment variable:

```shell
set ANONFILESNEW_API_KEY=YOUR_API_KEY
python -m fileuploader upload --service anonfilesnew path/to/file.txt --api-key-env ANONFILESNEW_API_KEY
```

Launch the desktop GUI:

```shell
python -m fileuploader_gui
```

Launch the terminal UI:

```shell
python -m fileuploader_tui
```

## CLI Reference

```shell
python -m fileuploader services [--json] [--active-only]
python -m fileuploader upload PATH --service SERVICE [--api-key KEY] [--api-key-env ENV] [--json] [--plaintext] [--copy] [--verbose]
python -m fileuploader download --service SERVICE [--url URL] [--server SERVER --file-id FILE_ID --filename NAME] [--json]
python -m fileuploader info FILE_ID --service SERVICE [--api-key KEY] [--api-key-env ENV] [--json]
```

See [docs/interfaces.md](docs/interfaces.md) for the interface design notes and framework comparison.

## Supported Providers

| Provider | Service name | Upload | Download | Info | API key | Status |
| --- | --- | --- | --- | --- | --- | --- |
| GoFile | `gofile` | Yes | Yes | No | No | Active |
| AnonFilesNew | `anonfilesnew` | Yes | No | Yes | Yes | Active |
| JSONBin | `jsonbin` | Yes | No | No | Yes | Active |
| AnonFiles | `anonfiles` | Yes | No | No | No | Deprecated |
| BayFiles | `bayfiles` | Yes | No | No | No | Deprecated |

## Provider-Specific Notes

### GoFile

GoFile supports upload and download through the unified CLI. The legacy GoFile entrypoint also supports local encryption, local decryption, output formatting, and clipboard copying:

```shell
python GoFile/main.py -u path/to/file.txt --encrypt --password "your-password"
python GoFile/main.py --decrypt-file file.txt.enc --password "your-password" --decrypt-output file.txt
```

### AnonFilesNew

AnonFilesNew requires an API key for account uploads. Use `--api-key` or `--api-key-env ANONFILESNEW_API_KEY`.

Legacy entrypoint:

```shell
python AnonFilesNew.com/anonfilesnew.py path/to/file.txt --api-key YOUR_API_KEY --json
```

### JSONBin

JSONBin stores file content as JSON records and requires an API key. The provider also has a chunk uploader for larger workflows:

```shell
python JSONBin.com/jsonbin_uploader.py upload path/to/file.txt --api-key YOUR_API_KEY --manifest upload-manifest.json
```

Use multiple JSONBin keys by repeating `--api-key` or setting `JSONBIN_API_KEYS` with comma-separated values.

## Development

Run the full test suite:

```shell
python -m unittest discover -s tests
```

Compile the main modules:

```shell
python -m py_compile fileuploader/*.py fileuploader_gui.py fileuploader_tui.py
```

Expected local smoke checks:

```shell
python -m fileuploader services --json
python -c "from fileuploader_tui import service_table; print(len(service_table().rows))"
python -c "import fileuploader_gui; print(fileuploader_gui.default_state())"
```

## Project Layout

```text
fileuploader/       Shared provider core, registry, formatters, and CLI
fileuploader_gui.py Tkinter desktop interface
fileuploader_tui.py Rich terminal interface
GoFile/             Legacy GoFile scripts and encryption helpers
AnonFilesNew.com/   Legacy AnonFilesNew scripts
JSONBin.com/        JSONBin chunk uploader
tests/              Unit and smoke tests
docs/               Interface documentation
```

## Contributing

Pull requests are welcome. For larger changes, open an issue first with the intended behavior, provider impact, and validation plan.

## License

[MIT](LICENSE)
