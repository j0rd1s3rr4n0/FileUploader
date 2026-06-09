# FileUploader Interfaces

FileUploader now exposes one shared provider core through three user interfaces:

- `python -m fileuploader_cli` for command-line automation.
- `python -m fileuploader_gui` for a lightweight desktop workflow.
- `python -m fileuploader_tui` for terminal-guided interactive use.

`python -m fileuploader` remains available as an equivalent package entrypoint for the same CLI.

Credits are shown in the terminal banner and desktop headers:

- j0rd1s3rr4n0
- jordiserrano.me
- github.com/j0rd1s3rr4n0

## CLI

The primary CLI is built with Typer:

```shell
python -m fileuploader_cli services
python -m fileuploader_cli --no-banner services
python -m fileuploader_cli guided
python -m fileuploader_cli upload --service gofile path/to/file.txt --json
python -m fileuploader_cli upload --service moonpush path/to/file.txt
python -m fileuploader_cli upload --service tmpfilelink path/to/file.txt
python -m fileuploader_cli info --service anonfilesnew FILE_ID --api-key YOUR_API_KEY
```

Use `python -m fileuploader_cli guided` for a step-by-step flow that shows providers, asks for an action, and prompts only for the fields needed by that action.

Use `--no-banner` before the command when you want machine-friendly human output without the banner. JSON output never includes the banner.

For quick temporary sharing, prefer the no-registration providers such as `moonpush`, `0x0`, `tempsh`, `tmpfilelink`, `blipbin`, `easysend`, `dropfiledev`, `cupload`, and `qurl`.

For account-backed storage, use `box`, `dropbox`, or `mediafire` with `--api-key` or `--api-key-env`. `mega` is shown as disabled until a MEGAcmd or SDK-backed implementation is added.

Typer is used because it provides a modern command surface while building on Click internally. Click is therefore covered as the underlying command framework. The older argparse scripts remain available as legacy provider-specific entrypoints, but new automation should use `python -m fileuploader`.

## GUI

The GUI uses Tkinter because it ships with Python on Windows and does not require a heavy desktop dependency.

```shell
python -m fileuploader_gui
```

Use it when users prefer selecting the provider, file, action, and output format from a desktop window.

## TUI

The TUI uses Rich for readable terminal tables, prompts, and result panels.

```shell
python -m fileuploader_tui
```

Use it when users want an interactive terminal flow without remembering command flags.

## Validation

Run the full local validation suite with:

```shell
python -m unittest discover -s tests
python -m py_compile fileuploader/*.py fileuploader_cli.py fileuploader_gui.py fileuploader_tui.py
```
