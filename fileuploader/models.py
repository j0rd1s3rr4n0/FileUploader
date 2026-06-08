from dataclasses import asdict, dataclass, field
from typing import Any


class ProviderError(RuntimeError):
    def __init__(self, provider: str, message: str, code: str | None = None):
        super().__init__(message)
        self.provider = provider
        self.message = message
        self.code = code

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "message": self.message,
            "code": self.code,
        }


@dataclass(frozen=True)
class ProviderInfo:
    name: str
    display_name: str
    active: bool = True
    supports_upload: bool = True
    supports_download: bool = False
    supports_info: bool = False
    requires_api_key: bool = False
    deprecated: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class UploadResult:
    provider: str
    status: bool
    url: str | None = None
    short_url: str | None = None
    file_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    raw: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
