import argparse
import base64
import hashlib
import json
import os
import time
import uuid
from pathlib import Path

import requests


JSONBIN_CREATE_URL = "https://api.jsonbin.io/v3/b"
DEFAULT_CHUNK_SIZE = 500 * 1024
API_KEYS_ENV = "JSONBIN_API_KEYS"


def parse_size(value):
    text = value.strip().lower()
    units = {
        "b": 1,
        "kb": 1024,
        "mb": 1024 * 1024,
    }
    for suffix, multiplier in sorted(units.items(), key=lambda item: len(item[0]), reverse=True):
        if text.endswith(suffix):
            return int(float(text[: -len(suffix)]) * multiplier)
    return int(text)


def parse_api_keys(values):
    keys = []
    for value in values:
        keys.extend(part.strip() for part in value.split(",") if part.strip())

    env_value = os.environ.get(API_KEYS_ENV, "")
    keys.extend(part.strip() for part in env_value.split(",") if part.strip())
    return keys


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(filepath):
    digest = hashlib.sha256()
    with Path(filepath).open("rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def iter_file_chunks(filepath, chunk_size):
    with Path(filepath).open("rb") as file_handle:
        index = 0
        while True:
            chunk = file_handle.read(chunk_size)
            if not chunk:
                break
            yield index, chunk
            index += 1


def build_chunk_record(file_id, file_path, file_hash, total_parts, chunk_index, chunk_data):
    return {
        "upload_id": file_id,
        "file_id": file_id,
        "original_filename": file_path.name,
        "total_parts": total_parts,
        "part_index": chunk_index,
        "chunk_size": len(chunk_data),
        "chunk_sha256": sha256_bytes(chunk_data),
        "file_sha256": file_hash,
        "uploaded_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "content_encoding": "base64",
        "content": base64.b64encode(chunk_data).decode("ascii"),
    }


def create_jsonbin_record(record, api_key, bin_name=None, private=True, collection_id=None):
    headers = {
        "Content-Type": "application/json",
        "X-Master-Key": api_key,
        "X-Bin-Private": "true" if private else "false",
    }
    if bin_name:
        headers["X-Bin-Name"] = bin_name[:128]
    if collection_id:
        headers["X-Collection-Id"] = collection_id

    response = requests.post(JSONBIN_CREATE_URL, headers=headers, json=record, timeout=60)
    try:
        payload = response.json()
    except ValueError:
        response.raise_for_status()
        raise

    if response.status_code >= 400:
        message = payload.get("message", response.text)
        raise RuntimeError(message)
    return payload


def create_jsonbin_record_with_retries(record, api_keys, key_start_index, args, bin_name):
    errors = []
    attempts = max(1, args.retry_attempts + 1)

    for attempt in range(attempts):
        api_key_index = (key_start_index + attempt) % len(api_keys)
        api_key = api_keys[api_key_index]
        try:
            response = create_jsonbin_record(
                record,
                api_key,
                bin_name=bin_name,
                private=not args.public,
                collection_id=args.collection_id,
            )
            return response, api_key_index, attempt
        except (requests.RequestException, RuntimeError) as exc:
            errors.append(str(exc))
            if attempt < attempts - 1 and args.retry_delay > 0:
                time.sleep(args.retry_delay)

    raise RuntimeError("; ".join(errors))


def upload_file(args):
    file_path = Path(args.file)
    if not file_path.is_file():
        raise FileNotFoundError(f"File not found: {args.file}")

    api_keys = parse_api_keys(args.api_key)
    if not api_keys:
        raise ValueError(f"Provide at least one API key with --api-key or {API_KEYS_ENV}")

    chunk_size = parse_size(args.chunk_size)
    if chunk_size <= 0:
        raise ValueError("Chunk size must be greater than zero")

    file_size = file_path.stat().st_size
    total_parts = (file_size + chunk_size - 1) // chunk_size
    file_id = args.upload_id or str(uuid.uuid4())
    file_hash = sha256_file(file_path)
    uploaded_parts = []
    failed_parts = []

    for chunk_index, chunk_data in iter_file_chunks(file_path, chunk_size):
        record = build_chunk_record(file_id, file_path, file_hash, total_parts, chunk_index, chunk_data)
        key_start_index = chunk_index % len(api_keys)
        bin_name = f"{file_path.name}-{file_id}-part-{chunk_index + 1}-of-{total_parts}"

        try:
            response, api_key_index, retry_count = create_jsonbin_record_with_retries(
                record,
                api_keys,
                key_start_index,
                args,
                bin_name,
            )
            metadata = response.get("metadata", {})
            uploaded_parts.append(
                {
                    "part_index": chunk_index,
                    "bin_id": metadata.get("id"),
                    "chunk_sha256": record["chunk_sha256"],
                    "chunk_size": record["chunk_size"],
                    "api_key_index": api_key_index,
                    "retry_count": retry_count,
                }
            )
            if args.verbose:
                print(f"Uploaded part {chunk_index + 1}/{total_parts}: {metadata.get('id')}")
        except (requests.RequestException, RuntimeError) as exc:
            failed_parts.append({"part_index": chunk_index, "error": str(exc)})
            if args.verbose:
                print(f"Failed part {chunk_index + 1}/{total_parts}: {exc}")
            if len(failed_parts) > args.max_failures:
                break

    manifest = {
        "upload_id": file_id,
        "file_id": file_id,
        "original_filename": file_path.name,
        "file_size": file_size,
        "file_sha256": file_hash,
        "chunk_size": chunk_size,
        "total_parts": total_parts,
        "uploaded_parts": uploaded_parts,
        "failed_parts": failed_parts,
        "complete": len(uploaded_parts) == total_parts and not failed_parts,
    }

    if args.manifest:
        Path(args.manifest).write_text(json.dumps(manifest, indent=4), encoding="utf-8")

    return manifest


def reconstruct_from_manifest(args):
    manifest = json.loads(Path(args.manifest_file).read_text(encoding="utf-8"))
    parts_dir = Path(args.parts_dir)
    output_path = Path(args.output or manifest["original_filename"])
    expected_parts = manifest["total_parts"]

    with output_path.open("wb") as output:
        for index in range(expected_parts):
            part_path = parts_dir / f"{index}.part"
            if not part_path.is_file():
                raise FileNotFoundError(f"Missing chunk file: {part_path}")
            data = part_path.read_bytes()
            output.write(data)

    actual_hash = sha256_file(output_path)
    if actual_hash != manifest["file_sha256"]:
        raise ValueError("Reconstructed file hash does not match manifest")

    return {
        "output": str(output_path),
        "file_sha256": actual_hash,
        "verified": True,
    }


def parse_args():
    parser = argparse.ArgumentParser(description="Upload file chunks to JSONBin.io")
    subparsers = parser.add_subparsers(dest="command", required=True)

    upload = subparsers.add_parser("upload", help="Split a file and upload chunks to JSONBin")
    upload.add_argument("file", help="File to upload")
    upload.add_argument("--api-key", action="append", default=[], help="JSONBin API key. Can be repeated or comma-separated")
    upload.add_argument("--chunk-size", default=str(DEFAULT_CHUNK_SIZE), help="Chunk size in bytes, KB, or MB")
    upload.add_argument("--upload-id", help="Logical upload/file id. Defaults to a UUID")
    upload.add_argument("--manifest", help="Write upload manifest to this JSON file")
    upload.add_argument("--collection-id", help="Optional JSONBin collection id")
    upload.add_argument("--public", action="store_true", help="Create public bins instead of private bins")
    upload.add_argument("--max-failures", type=int, default=0, help="Abort after more than this many failed chunks")
    upload.add_argument("--retry-attempts", type=int, default=3, help="Retry attempts per chunk")
    upload.add_argument("--retry-delay", type=float, default=1.0, help="Seconds to wait between retries")
    upload.add_argument("--verbose", action="store_true", help="Print upload progress")

    reconstruct = subparsers.add_parser("reconstruct-manifest", help="Reconstruct local chunk files using a manifest")
    reconstruct.add_argument("manifest_file", help="Manifest JSON file")
    reconstruct.add_argument("--parts-dir", required=True, help="Directory containing chunk files named 0.part, 1.part, ...")
    reconstruct.add_argument("--output", help="Output file path")

    return parser.parse_args()


def main():
    args = parse_args()
    try:
        if args.command == "upload":
            result = upload_file(args)
        elif args.command == "reconstruct-manifest":
            result = reconstruct_from_manifest(args)
        else:
            raise ValueError(f"Unknown command: {args.command}")
    except (OSError, ValueError, RuntimeError, requests.RequestException) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=4))
        return 1

    print(json.dumps({"ok": True, "result": result}, indent=4))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
