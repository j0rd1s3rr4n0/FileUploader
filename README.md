# FileUploader

Unified Python tooling for uploading files through CLI, GUI, and TUI workflows.

[![Python](https://img.shields.io/badge/python-3.10%2B-2563eb.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-047857.svg)](LICENSE)
[![Providers](https://img.shields.io/badge/providers-25-0f766e.svg)](#provider-matrix)
[![Interfaces](https://img.shields.io/badge/interfaces-CLI%20%7C%20GUI%20%7C%20TUI-111827.svg)](#interfaces)
[![Validation](https://img.shields.io/badge/tests-unittest-7c3aed.svg)](#development)

FileUploader gives you one normalized upload core for temporary file hosts, cloud-backed providers, and legacy upload scripts. Use it from a modern CLI, a lightweight desktop GUI, or a Rich-powered terminal UI.

Created by **j0rd1s3rr4n0**: [jordiserrano.me](https://jordiserrano.me) | [github.com/j0rd1s3rr4n0](https://github.com/j0rd1s3rr4n0)

## Why FileUploader

Most file hosts expose different request shapes, response formats, and failure messages. FileUploader wraps them behind one interface with normalized provider metadata, upload results, and errors.

| What you need | Use this |
| --- | --- |
| Quick public link, no account | `exploitsend`, `catbox`, `fileio`, `0x0`, `tempsh`, `transfersh`, `gofile` |
| Automation and scripting | `python -m fileuploader_cli ... --json --no-banner` |
| Desktop workflow | `python -m fileuploader_gui` |
| Interactive terminal flow | `python -m fileuploader_tui` |
| Account-backed storage | `4shared`, `box`, `dropbox`, `mediafire`, `jsonbin`, `anonfilesnew` |

## Interfaces

| Interface | Command | Best for |
| --- | --- | --- |
| CLI | `python -m fileuploader_cli` | Scripts, CI jobs, JSON output, repeatable commands |
| Package CLI | `python -m fileuploader` | Equivalent package entrypoint for the same CLI |
| GUI | `python -m fileuploader_gui` | Provider-aware desktop uploads and copyable results |
| TUI | `python -m fileuploader_tui` | Guided terminal use with Rich tables and prompts |

## Quick Start

Install dependencies:

```shell
git clone https://github.com/j0rd1s3rr4n0/FileUploader.git
cd FileUploader
python -m pip install -r requirements.txt
```

List providers:

```shell
python -m fileuploader_cli services
```

Upload without registration:

```shell
python -m fileuploader_cli upload --service catbox path/to/file.txt
```

Upload with JSON output for scripts:

```shell
python -m fileuploader_cli upload --service gofile path/to/file.txt --json
```

Hide the banner for automation:

```shell
python -m fileuploader_cli --no-banner services
```

Launch the desktop GUI:

```shell
python -m fileuploader_gui
```

Launch the terminal UI:

```shell
python -m fileuploader_tui
```

## Common Workflows

### No Account Required

Use these first when you just need a public link and do not want to create an account or pass tokens:

```shell
python -m fileuploader_cli upload --service catbox path/to/file.txt
python -m fileuploader_cli upload --service fileio path/to/file.txt
python -m fileuploader_cli upload --service exploitsend path/to/file.txt
python -m fileuploader_cli upload --service exploitsend path/to/file.txt --password secret --ttl 3600 --max-downloads 3
python -m fileuploader_cli upload --service 0x0 path/to/file.txt
python -m fileuploader_cli upload --service transfersh path/to/file.txt
python -m fileuploader_cli upload --service tempsh path/to/file.txt
```

### Copy-Friendly Output

Human output is readable by default. JSON output is clean and banner-free:

```shell
python -m fileuploader_cli upload --service gofile path/to/file.txt --json
```

Some workflows also support copying processed output:

```shell
python -m fileuploader_cli upload --service catbox path/to/file.txt --copy
```

### API Keys and Tokens

Pass credentials directly:

```shell
python -m fileuploader_cli upload --service anonfilesnew path/to/file.txt --api-key YOUR_API_KEY
python -m fileuploader_cli upload --service box path/to/file.txt --api-key BOX_OAUTH_ACCESS_TOKEN
python -m fileuploader_cli upload --service 4shared path/to/file.txt --api-key "oauth_token=...&oauth_signature=..."
```

Or read them from environment variables:

```shell
set ANONFILESNEW_API_KEY=YOUR_API_KEY
python -m fileuploader_cli upload --service anonfilesnew path/to/file.txt --api-key-env ANONFILESNEW_API_KEY
```

### Guided CLI

When you do not remember the flags, use the guided flow:

```shell
python -m fileuploader_cli guided
```

## CLI Reference

```shell
python -m fileuploader_cli [--no-banner] services [--json] [--active-only]
python -m fileuploader_cli [--no-banner] guided
python -m fileuploader_cli [--no-banner] upload PATH --service SERVICE [--api-key KEY] [--api-key-env ENV] [--json] [--plaintext] [--copy] [--verbose]
python -m fileuploader_cli [--no-banner] download --service SERVICE [--url URL] [--server SERVER --file-id FILE_ID --filename NAME] [--json]
python -m fileuploader_cli [--no-banner] info FILE_ID --service SERVICE [--api-key KEY] [--api-key-env ENV] [--json]
```

## Preview

CLI service list:

```text
Service       Upload  Download  Info  API key  Status
------------  ------  --------  ----  -------  ------
catbox        yes     no        no    no       active
fileio        yes     no        no    no       active
gofile        yes     yes       no    no       active
jsonbin       yes     no        no    yes      active
mega          no      no        no    yes      disabled
```

GUI workflow:

```text
Choose provider -> choose action -> enter only required fields -> run -> copy result
```

TUI workflow:

```text
Rich provider table -> guided prompts -> normalized result panel
```

## Features

| Feature | Description |
| --- | --- |
| Unified provider core | One interface for provider metadata, upload results, and provider errors. |
| Provider-aware UX | CLI, GUI, and TUI ask only for the fields needed by the selected action. |
| No-registration providers | Many services work without account creation or API keys. |
| Account-backed providers | Box, Dropbox, MediaFire, JSONBin, and AnonFilesNew support token/key workflows. |
| JSON automation | `--json` returns parseable output without banner text. |
| Script-friendly banner control | `--no-banner` hides the terminal banner for automation. |
| Clipboard support | Copy supported outputs directly from CLI/GUI flows. |
| GoFile encryption workflow | Legacy GoFile scripts support AES-GCM encrypt/decrypt helpers. |
| Testable design | Tests use mocked providers and avoid real network calls. |

## Provider Matrix

| Provider | Service | Upload | Download | Info | API key | Status |
| --- | --- | --- | --- | --- | --- | --- |
| 0x0.st | `0x0` | Yes | No | No | No | Active |
| 4shared | `4shared` | Yes | No | Yes | Yes | Active |
| AnonFilesNew | `anonfilesnew` | Yes | No | Yes | Yes | Active |
| blipbin | `blipbin` | Yes | No | No | No | Active |
| Box | `box` | Yes | No | Yes | Yes | Active |
| Catbox | `catbox` | Yes | No | No | No | Active |
| cupload.io | `cupload` | Yes | No | No | No | Active |
| Dropbox | `dropbox` | Yes | No | Yes | Yes | Active |
| dropfile.dev | `dropfiledev` | Yes | No | No | No | Active |
| EasySend | `easysend` | Yes | No | No | No | Active |
| Exploit.IN Send | `exploitsend` | Yes | No | Yes | No | Active |
| file.io | `fileio` | Yes | No | No | No | Active |
| GoFile | `gofile` | Yes | Yes | No | No | Active |
| JSONBin | `jsonbin` | Yes | No | No | Yes | Active |
| Litterbox | `litterbox` | Yes | No | No | No | Active |
| MediaFire | `mediafire` | Yes | No | No | Yes | Active |
| MoonPush | `moonpush` | Yes | No | Yes | No | Active |
| qurl.sh | `qurl` | Yes | No | No | No | Active |
| Temp.sh | `tempsh` | Yes | No | No | No | Active |
| tmpfile.link | `tmpfilelink` | Yes | No | No | No | Active |
| transfer.sh | `transfersh` | Yes | No | No | No | Active |
| Uguu | `uguu` | Yes | No | No | No | Active |
| MEGA | `mega` | No | No | No | Yes | Disabled |
| AnonFiles | `anonfiles` | Yes | No | No | No | Deprecated |
| BayFiles | `bayfiles` | Yes | No | No | No | Deprecated |

## Provider Notes

### Recommended No-Registration Providers

| Service | Good for |
| --- | --- |
| `catbox` | Simple public file links |
| `exploitsend` | Client-side encrypted links |
| `fileio` | Temporary links with JSON responses |
| `0x0` | Minimal terminal uploads |
| `tempsh` | Temporary file sharing |
| `transfersh` | Terminal-first uploads via PUT |
| `gofile` | Upload plus basic download support |

Retention, file size limits, rate limits, and content policies are controlled by each upstream provider.

`exploitsend` encrypts locally before upload using AES-GCM and returns a link with the decryption key after `#`, matching the web app's client-side format.

### Account-Backed Providers

| Service | Credential |
| --- | --- |
| `4shared` | OAuth query parameters |
| `anonfilesnew` | API key |
| `box` | OAuth access token |
| `dropbox` | OAuth access token |
| `jsonbin` | JSONBin API key |
| `mediafire` | MediaFire session token |

Prefer `--api-key-env` for repeat usage so secrets stay outside shell history.

For `4shared`, pass the already signed OAuth query string through `--api-key` or `FOURSHARED_OAUTH_PARAMS`. The provider uses the simple upload endpoint for files below 150 MB and uploads to folder `0` unless a future interface supplies a different `folder_id`.

### Disabled and Deprecated Providers

Disabled providers are shown in service lists but are not offered as active GUI choices. Deprecated providers remain available for compatibility, but upstream APIs may fail or disappear.

MEGA is currently disabled because reliable uploads need MEGAcmd or an SDK-backed implementation rather than a simple HTTP upload endpoint.

## Security and Privacy

- Treat public upload links as public unless the provider explicitly says otherwise.
- Do not upload secrets, private keys, credentials, or sensitive personal data to public hosts.
- Prefer environment variables for tokens and API keys.
- FileUploader normalizes provider responses, but storage, deletion, retention, and abuse policies belong to each upstream service.
- Local tests use mocked HTTP clients and do not upload files.

## Legacy Workflows

The unified interfaces should be the default for new usage. Legacy provider scripts remain available for specialized flows.

GoFile encryption helpers:

```shell
python GoFile/main.py -u path/to/file.txt --encrypt --password "your-password"
python GoFile/main.py --decrypt-file file.txt.enc --password "your-password" --decrypt-output file.txt
```

AnonFilesNew legacy entrypoint:

```shell
python AnonFilesNew.com/anonfilesnew.py path/to/file.txt --api-key YOUR_API_KEY --json
```

JSONBin chunk uploader:

```shell
python JSONBin.com/jsonbin_uploader.py upload path/to/file.txt --api-key YOUR_API_KEY --manifest upload-manifest.json
```

## Development

Install locally:

```shell
git clone https://github.com/j0rd1s3rr4n0/FileUploader.git
cd FileUploader
python -m pip install -r requirements.txt
```

Run tests:

```shell
python -m unittest discover -s tests
```

Compile modules:

```shell
python -m compileall fileuploader fileuploader_cli.py fileuploader_gui.py fileuploader_tui.py
```

Smoke checks:

```shell
python -m fileuploader_cli services --json
python -m fileuploader_cli --no-banner services
python -c "from fileuploader_tui import service_table; print(len(service_table().rows))"
python -c "import fileuploader_gui; print(fileuploader_gui.default_state())"
```

Project layout:

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

## Roadmap

Planned improvements:

- Provider health checks and capability reporting.
- Batch uploads across CLI, GUI, and TUI.
- Local upload history with export.
- Config profiles for defaults and environment variable names.
- Retry, timeout, and backoff policy.
- Output formats for URL-only, Markdown, HTML, text, and JSON.
- Packaging with installable console commands.

## Contributing

Pull requests are welcome. For larger changes, open an issue with:

- the user-facing behavior;
- affected providers or interfaces;
- expected tests;
- compatibility risks.

Keep new providers behind the shared provider core and cover them with mocked tests.

## License

[MIT](LICENSE)
