import argparse
import json
import os
import sys
from pathlib import Path
from tkinter import Tk
from tkinter.filedialog import askopenfilename

import requests


UPLOAD_URL = "https://api.anonfilesnew.com/upload"
API_KEY_ENV = "ANONFILESNEW_API_KEY"


def choose_file():
    Tk().withdraw()
    filename = askopenfilename(
        title="AnonFilesNew Upload File",
        filetypes=[("All files", "*.*")],
    )
    return filename or None


def upload_file(filepath, api_key):
    path = Path(filepath)
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {filepath}")

    with path.open("rb") as file_handle:
        response = requests.post(
            UPLOAD_URL,
            params={"key": api_key},
            files={"file": (path.name, file_handle)},
            timeout=120,
        )
    try:
        payload = response.json()
    except ValueError:
        response.raise_for_status()
        raise

    if not payload.get("status"):
        error = payload.get("error", {})
        message = error.get("message", "Unknown upload error")
        raise RuntimeError(message)

    return payload


def print_result(payload, as_json=False):
    if as_json:
        print(json.dumps(payload, indent=4))
        return

    file_data = payload["data"]["file"]
    url = file_data.get("url", {})
    metadata = file_data.get("metadata", {})
    size = metadata.get("size", {})

    print(f"FULL URL: {url.get('full', '')}")
    print(f"SHORT URL: {url.get('short', '')}")
    print("[ FILE INFO ]")
    print(f"ID: {metadata.get('id', '')}")
    print(f"FILE NAME: {metadata.get('name', '')}")
    print("SIZE:")
    print(f"    BYTES: {size.get('bytes', '')}")
    print(f"    READABLE: {size.get('readable', '')}")


def parse_args():
    parser = argparse.ArgumentParser(description="Upload a file to anonfilesnew.com")
    parser.add_argument("filepath", nargs="?", help="Path to the file to upload")
    parser.add_argument(
        "--api-key",
        default=None,
        help=f"AnonFilesNew API key. Defaults to ${API_KEY_ENV}",
    )
    parser.add_argument("--json", action="store_true", help="Print the raw JSON response")
    return parser.parse_args()


def main():
    args = parse_args()
    filepath = args.filepath or choose_file()
    if not filepath:
        print("No file selected.")
        return 1
    api_key = args.api_key or os.environ.get(API_KEY_ENV)
    if not api_key:
        print(f"Missing API key. Use --api-key or set {API_KEY_ENV}.", file=sys.stderr)
        return 1

    try:
        payload = upload_file(filepath, api_key)
    except requests.RequestException as exc:
        print(f"Upload request failed: {exc}", file=sys.stderr)
        return 1
    except (OSError, RuntimeError, ValueError, KeyError) as exc:
        print(f"Upload failed: {exc}", file=sys.stderr)
        return 1

    print_result(payload, args.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
