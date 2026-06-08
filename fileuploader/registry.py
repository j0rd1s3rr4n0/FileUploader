from .models import ProviderError
from .providers import (
    AnonFilesNewProvider,
    AnonFilesProvider,
    BayFilesProvider,
    GoFileProvider,
    JsonBinProvider,
)


class ProviderRegistry:
    def __init__(self, providers=None):
        self._providers = {}
        for provider in providers or []:
            self.register(provider)

    def register(self, provider):
        self._providers[provider.info.name] = provider

    def get(self, name):
        try:
            return self._providers[name]
        except KeyError as exc:
            choices = ", ".join(sorted(self._providers))
            raise ProviderError(name, f"Unknown provider '{name}'. Available providers: {choices}") from exc

    def providers(self):
        return [self._providers[name] for name in sorted(self._providers)]


def create_default_registry():
    return ProviderRegistry(
        [
            GoFileProvider(),
            AnonFilesNewProvider(),
            JsonBinProvider(),
            AnonFilesProvider(),
            BayFilesProvider(),
        ]
    )
