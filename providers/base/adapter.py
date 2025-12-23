from __future__ import annotations

import logging
from typing import Mapping

import requests
from requests import Session

from smart_common.providers.exceptions import ProviderFetchError

logger = logging.getLogger(__name__)


class BaseHttpAdapter:
    """
    Low-level HTTP adapter.
    Handles:
    - base URL
    - requests.Session
    - retries
    - transport-level errors

    DOES NOT:
    - implement auth logic
    - interpret response payloads
    """

    def __init__(
        self,
        base_url: str,
        *,
        headers: Mapping[str, str] | None = None,
        timeout: float = 10.0,
        max_retries: int = 3,
    ) -> None:
        if not base_url:
            raise ValueError("base_url is required")

        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max(1, max_retries)

        self.session: Session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/json",
                **(headers or {}),
            }
        )

    # ------------------------------------------------------------------
    # Core request helper
    # ------------------------------------------------------------------
    def _request(
        self,
        method: str,
        path: str,
        *,
        json_data: dict | None = None,
    ) -> requests.Response:
        url = self._url(path)
        last_exc: Exception | None = None

        for attempt in range(1, self.max_retries + 1):
            try:
                logger.debug(
                    "HTTP request attempt %s/%s",
                    attempt,
                    self.max_retries,
                    extra={
                        "method": method,
                        "url": url,
                    },
                )

                return self.session.request(
                    method,
                    url,
                    json=json_data,
                    timeout=self.timeout,
                )

            except requests.Timeout as exc:
                last_exc = exc
                logger.warning(
                    "HTTP timeout",
                    extra={"url": url, "attempt": attempt},
                )

            except requests.RequestException as exc:
                last_exc = exc
                logger.warning(
                    "HTTP request error",
                    extra={"url": url, "attempt": attempt, "error": str(exc)},
                )

        logger.error(
            "HTTP request failed after retries",
            extra={"url": url, "retries": self.max_retries},
        )

        raise ProviderFetchError(
            "HTTP request failed after retries",
            details={"error": str(last_exc)},
        )

    # ------------------------------------------------------------------
    # Utils
    # ------------------------------------------------------------------
    def _url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

    def close(self) -> None:
        self.session.close()
