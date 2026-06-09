# FileUploader

Unified Python tooling for uploading files to multiple file-hosting providers.

[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-active-success.svg)](#supported-providers)

FileUploader provides a shared provider layer plus three user interfaces:

- **CLI** for automation and scripts: `python -m fileuploader_cli`
- **GUI** for desktop users: `python -m fileuploader_gui`
- **TUI** for guided terminal use: `python -m fileuploader_tui`

`python -m fileuploader` is kept as an equivalent package entrypoint for the same CLI.

Created by **j0rd1s3rr4n0**: [jordiserrano.me](https://jordiserrano.me) | [github.com/j0rd1s3rr4n0](https://github.com/j0rd1s3rr4n0)

The current provider set includes GoFile, a broad no-registration upload set, and account-backed cloud providers such as Box, Dropbox, MediaFire, and MEGA. Deprecated providers remain available for compatibility, but upstream APIs may be unreliable.

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
python -m fileuploader_cli services
```

Hide the terminal banner and credits when scripting:

```shell
python -m fileuploader_cli --no-banner services
```

Use the guided CLI when you do not remember the flags:

```shell
python -m fileuploader_cli guided
```

Upload a file with GoFile and print JSON:

```shell
python -m fileuploader_cli upload --service gofile path/to/file.txt --json
```

Upload without registration:

```shell
python -m fileuploader_cli upload --service moonpush path/to/file.txt
python -m fileuploader_cli upload --service 0x0 path/to/file.txt
python -m fileuploader_cli upload --service tmpfilelink path/to/file.txt
```

Upload with AnonFilesNew using an API key:

```shell
python -m fileuploader_cli upload --service anonfilesnew path/to/file.txt --api-key YOUR_API_KEY --json
```

Use an API key from an environment variable:

```shell
set ANONFILESNEW_API_KEY=YOUR_API_KEY
python -m fileuploader_cli upload --service anonfilesnew path/to/file.txt --api-key-env ANONFILESNEW_API_KEY
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
python -m fileuploader_cli [--no-banner] services [--json] [--active-only]
python -m fileuploader_cli [--no-banner] guided
python -m fileuploader_cli [--no-banner] upload PATH --service SERVICE [--api-key KEY] [--api-key-env ENV] [--json] [--plaintext] [--copy] [--verbose]
python -m fileuploader_cli [--no-banner] download --service SERVICE [--url URL] [--server SERVER --file-id FILE_ID --filename NAME] [--json]
python -m fileuploader_cli [--no-banner] info FILE_ID --service SERVICE [--api-key KEY] [--api-key-env ENV] [--json]
```

See [docs/interfaces.md](docs/interfaces.md) for the interface design notes and framework comparison.

## Supported Providers

| Provider | Service name | Upload | Download | Info | API key | Status |
| --- | --- | --- | --- | --- | --- | --- |
| GoFile | `gofile` | Yes | Yes | No | No | Active |
| 0x0.st | `0x0` | Yes | No | No | No | Active |
| MoonPush | `moonpush` | Yes | No | Yes | No | Active |
| Temp.sh | `tempsh` | Yes | No | No | No | Active |
| tmpfile.link | `tmpfilelink` | Yes | No | No | No | Active |
| blipbin | `blipbin` | Yes | No | No | No | Active |
| EasySend | `easysend` | Yes | No | No | No | Active |
| dropfile.dev | `dropfiledev` | Yes | No | No | No | Active |
| cupload.io | `cupload` | Yes | No | No | No | Active |
| qurl.sh | `qurl` | Yes | No | No | No | Active |
| Box | `box` | Yes | No | Yes | Yes | Active |
| Dropbox | `dropbox` | Yes | No | Yes | Yes | Active |
| MediaFire | `mediafire` | Yes | No | No | Yes | Active |
| MEGA | `mega` | No | No | No | Yes | Disabled |
| AnonFilesNew | `anonfilesnew` | Yes | No | Yes | Yes | Active |
| JSONBin | `jsonbin` | Yes | No | No | Yes | Active |
| AnonFiles | `anonfiles` | Yes | No | No | No | Deprecated |
| BayFiles | `bayfiles` | Yes | No | No | No | Deprecated |

## Provider-Specific Notes

### No-registration providers

Use these when you want a quick public link without creating an account or passing API keys:

```shell
python -m fileuploader_cli upload --service moonpush path/to/file.txt
python -m fileuploader_cli upload --service tempsh path/to/file.txt
python -m fileuploader_cli upload --service blipbin path/to/file.txt
python -m fileuploader_cli upload --service dropfiledev path/to/file.txt
```

The no-registration providers are best for temporary sharing and automation. Retention, size limits, and rate limits are controlled by each upstream service.

### Account-backed cloud providers

Box, Dropbox, and MediaFire require account credentials or access tokens:

```shell
python -m fileuploader_cli upload --service box path/to/file.txt --api-key BOX_OAUTH_ACCESS_TOKEN
python -m fileuploader_cli upload --service dropbox path/to/file.txt --api-key DROPBOX_OAUTH_ACCESS_TOKEN
python -m fileuploader_cli upload --service mediafire path/to/file.txt --api-key MEDIAFIRE_SESSION_TOKEN
```

Environment variable shortcuts are also supported:

```shell
set BOX_ACCESS_TOKEN=...
set DROPBOX_ACCESS_TOKEN=...
set MEDIAFIRE_SESSION_TOKEN=...
python -m fileuploader_cli upload --service dropbox path/to/file.txt --api-key-env DROPBOX_ACCESS_TOKEN
```

MEGA is listed as disabled because reliable uploads require MEGAcmd or an SDK-backed implementation rather than a simple HTTP upload endpoint.

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
python -m py_compile fileuploader/*.py fileuploader_cli.py fileuploader_gui.py fileuploader_tui.py
```

Expected local smoke checks:

```shell
python -m fileuploader_cli services --json
python -m fileuploader_cli --no-banner services
python -c "from fileuploader_tui import service_table; print(len(service_table().rows))"
python -c "import fileuploader_gui; print(fileuploader_gui.default_state())"
```

## Project Layout

```text
fileuploader/       Shared provider core, registry, formatters, and CLI
fileuploader_cli.py CLI-only launcher
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
