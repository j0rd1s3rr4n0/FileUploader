from .models import ProviderError


def require_value(provider: str, value: str | None, message: str, code: str):
    if not value:
        raise ProviderError(provider, message, code=code)
