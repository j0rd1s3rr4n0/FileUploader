from collections.abc import Iterable

from .models import ProviderInfo
from .registry import ProviderRegistry, create_default_registry


class FileUploaderCore:
    def __init__(self, registry: ProviderRegistry | None = None):
        self.registry = registry or create_default_registry()

    def services(self, include_deprecated: bool = True) -> list[ProviderInfo]:
        providers: Iterable = self.registry.providers()
        if not include_deprecated:
            providers = [provider for provider in providers if provider.info.active and not provider.info.deprecated]
        return [provider.info for provider in providers]

    def upload(self, service: str, filepath: str, **options):
        return self.registry.get(service).upload(filepath, **options)

    def download(self, service: str, **options):
        return self.registry.get(service).download(**options)

    def info(self, service: str, file_id: str, **options):
        return self.registry.get(service).info_file(file_id, **options)
