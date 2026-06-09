import json
from dataclasses import asdict, is_dataclass
from typing import Any


def service_rows(services: list[dict[str, Any]]) -> str:
    headers = ["Service", "Upload", "Download", "Info", "API key", "Status"]
    rows = []
    for service in services:
        rows.append(
            [
                service["name"],
                "yes" if service["supports_upload"] else "no",
                "yes" if service["supports_download"] else "no",
                "yes" if service["supports_info"] else "no",
                "yes" if service["requires_api_key"] else "no",
                "disabled" if not service["active"] else "deprecated" if service["deprecated"] else "active",
            ]
        )
    widths = [len(header) for header in headers]
    for row in rows:
        for index, value in enumerate(row):
            widths[index] = max(widths[index], len(value))

    def render_row(values):
        return "  ".join(value.ljust(widths[index]) for index, value in enumerate(values))

    separator = "  ".join("-" * width for width in widths)
    return "\n".join([render_row(headers), separator, *[render_row(row) for row in rows]])


def to_plaintext(value: Any, indent: int = 0) -> str:
    if is_dataclass(value):
        value = asdict(value)
    if isinstance(value, list):
        return "".join(to_plaintext(item, indent) + ("\n" if index < len(value) - 1 else "") for index, item in enumerate(value))
    if isinstance(value, dict):
        lines = []
        for key, item in value.items():
            if isinstance(item, (dict, list)):
                lines.append(" " * indent + f"{key}:")
                lines.append(to_plaintext(item, indent + 2))
            else:
                lines.append(" " * indent + f"{key}: {item}")
        return "\n".join(lines)
    return " " * indent + str(value)


def to_json(value: Any) -> str:
    if is_dataclass(value):
        value = asdict(value)
    elif isinstance(value, list):
        value = [asdict(item) if is_dataclass(item) else item for item in value]
    return json.dumps(value, indent=4)


def format_output(value: Any, json_output: bool = False) -> str:
    return to_json(value) if json_output else to_plaintext(value)
