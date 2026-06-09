from .models import ProviderError
from .providers import (
    AnonFilesNewProvider,
    AnonFilesProvider,
    BayFilesProvider,
    BlipbinProvider,
    BoxProvider,
    CatboxProvider,
    CuploadProvider,
    DropFileDevProvider,
    DropboxProvider,
    EasySendProvider,
    FileIoProvider,
    GoFileProvider,
    JsonBinProvider,
    LitterboxProvider,
    MediaFireProvider,
    MegaProvider,
    MoonPushProvider,
    QurlProvider,
    TempShProvider,
    TmpFileLinkProvider,
    TransferShProvider,
    UguuProvider,
    ZeroXZeroProvider,
)


class ProviderRegistry:
    def __init__(self, providers=None):
        self._providers = {}
        for provider in providers or []:
            self.register(provider)

    def register(self, provider):
        self._providers[provider.info.name.lower()] = provider

    def get(self, name):
        normalized_name = name.lower()
        try:
            return self._providers[normalized_name]
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
            ZeroXZeroProvider(),
            MoonPushProvider(),
            TempShProvider(),
            TmpFileLinkProvider(),
            BlipbinProvider(),
            EasySendProvider(),
            DropFileDevProvider(),
            CuploadProvider(),
            QurlProvider(),
            FileIoProvider(),
            UguuProvider(),
            CatboxProvider(),
            LitterboxProvider(),
            TransferShProvider(),
            BoxProvider(),
            DropboxProvider(),
            MediaFireProvider(),
            MegaProvider(),
            AnonFilesProvider(),
            BayFilesProvider(),
        ]
    )
