from __future__ import annotations
from typing import Any, Mapping


class ProviderError(Exception):
    """Base error for provider related failures."""

    def __init__(
        self,
        *,
        message: str,
        status_code: int = 400,
        code: str = "PROVIDER_ERROR",
        details: Mapping[str, Any] | None = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.code = code
        self.details = details or {}
        super().__init__(message)


# ------------------------------------------------------------------
# Fetch / network / upstream errors
# ------------------------------------------------------------------
class ProviderFetchError(ProviderError):
    """Raised when fetching data from provider fails."""

    def __init__(
        self,
        message: str,
        *,
        details: Mapping[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=502,
            code="PROVIDER_FETCH_ERROR",
            details=details,
        )


# ------------------------------------------------------------------
# Invalid configuration / credentials / setup
# ------------------------------------------------------------------
class ProviderConfigError(ProviderError):
    """Raised when provider configuration is invalid."""

    def __init__(
        self,
        message: str,
        *,
        details: Mapping[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=400,
            code="PROVIDER_CONFIG_ERROR",
            details=details,
        )


# ------------------------------------------------------------------
# Unsupported provider / adapter missing
# ------------------------------------------------------------------
class ProviderNotSupportedError(ProviderError):
    """Raised when no adapter exists for provider/vendor."""

    def __init__(self, vendor: str):
        super().__init__(
            message=f"Provider '{vendor}' is not supported",
            status_code=404,
            code="PROVIDER_NOT_SUPPORTED",
        )
