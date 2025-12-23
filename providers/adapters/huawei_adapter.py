from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Mapping

from smart_common.providers.base.provider_adapter import BaseProviderAdapter
from smart_common.providers.exceptions import ProviderError, ProviderFetchError
from smart_common.providers.enums import ProviderKind, ProviderType, ProviderVendor
from smart_common.providers.provider_config.config import provider_settings

logger = logging.getLogger(__name__)


class HuaweiProviderAdapter(BaseProviderAdapter):
    provider_type = ProviderType.API
    vendor = ProviderVendor.HUAWEI
    kind = ProviderKind.POWER

    def __init__(
        self,
        username: str,
        password: str,
        *,
        base_url: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
    ) -> None:
        super().__init__(
            base_url or provider_settings.HUAWEI_BASE_URL,
            headers={"Content-Type": "application/json"},
            timeout=timeout or provider_settings.HUAWEI_TIMEOUT,
            max_retries=max_retries or provider_settings.HUAWEI_MAX_RETRIES,
        )

        self.username = username
        self.password = password
        self._logged_in = False
        self._token_expires_at: datetime | None = None

    # ------------------------------------------------------------------
    # Login handling
    # ------------------------------------------------------------------

    def _is_expired(self) -> bool:
        return (
            self._token_expires_at is not None
            and datetime.now(timezone.utc) >= self._token_expires_at
        )

    def _ensure_login(self) -> None:
        if not self._logged_in or self._is_expired():
            logger.info("Huawei login required")
            self._login()

    def _login(self) -> None:
        logger.info("Huawei login start")

        payload = {
            "userName": self.username,
            "systemCode": self.password,
        }

        try:
            response = self._request(
                "POST",
                "login",
                json_data=payload,
            )
        except ProviderFetchError:
            raise
        except Exception as exc:
            logger.exception("Huawei login unexpected error")
            raise ProviderFetchError(
                "Huawei login failed",
                details={"error": str(exc)},
            ) from exc

        if not response.ok:
            raise ProviderError(
                message="Huawei authentication failed",
                status_code=response.status_code,
                code="HUAWEI_AUTH_FAILED",
                details={"body": response.text},
            )

        result = response.json()
        if not result.get("success"):
            raise ProviderError(
                message="Huawei authentication rejected",
                status_code=401,
                code="HUAWEI_AUTH_REJECTED",
                details={
                    "message": result.get("message"),
                    "failCode": result.get("failCode"),
                },
            )

        xsrf = self.session.cookies.get("XSRF-TOKEN")
        if not xsrf:
            raise ProviderError(
                message="Huawei login missing XSRF token",
                status_code=502,
                code="HUAWEI_XSRF_MISSING",
            )

        self.session.headers["XSRF-TOKEN"] = xsrf
        self._logged_in = True
        self._token_expires_at = datetime.now(timezone.utc) + timedelta(minutes=25)

        logger.info("Huawei login OK")

    # ------------------------------------------------------------------
    # Internal POST helper (Huawei-specific)
    # ------------------------------------------------------------------

    def _post(self, endpoint: str, payload: dict | None = None) -> dict:
        self._ensure_login()

        response = self._request(
            "POST",
            endpoint,
            json_data=payload or {},
        )

        if response.status_code == 401:
            logger.warning("Huawei 401 → re-login")
            self._login()
            response = self._request("POST", endpoint, json_data=payload or {})

        result = response.json()

        if (
            result.get("message") == "USER_MUST_RELOGIN"
            or result.get("failCode") == 20010
        ):
            logger.warning("Huawei USER_MUST_RELOGIN → re-login")
            self._login()
            response = self._request("POST", endpoint, json_data=payload or {})
            result = response.json()

        if not result.get("success", False):
            raise ProviderError(
                message="Huawei API error",
                status_code=502,
                code="HUAWEI_API_ERROR",
                details={
                    "message": result.get("message"),
                    "failCode": result.get("failCode"),
                },
            )

        self._token_expires_at = datetime.now(timezone.utc) + timedelta(minutes=25)
        return result

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def list_stations(self) -> list[Mapping[str, Any]]:
        logger.info("Huawei → list stations")

        result = self._post("getStationList")
        stations = result.get("data", [])

        return [self._normalize_station(s) for s in stations]

    def list_devices(self, station_code: str) -> list[Mapping[str, Any]]:
        logger.info(
            "Huawei → list devices",
            extra={"station_code": station_code},
        )

        payload = {"stationCodes": station_code}
        result = self._post("getDevList", payload)
        devices = result.get("data", [])

        return [self._normalize_device(d) for d in devices]

    # ------------------------------------------------------------------
    # Normalization
    # ------------------------------------------------------------------

    def _normalize_station(self, raw: Mapping[str, Any]) -> Mapping[str, Any]:
        return {
            "station_code": raw.get("stationCode"),
            "name": raw.get("stationName"),
            "capacity_kw": raw.get("capacity"),
            "grid_connected_time": raw.get("gridConnectedTime"),
            "raw": dict(raw),
        }

    def _normalize_device(self, raw: Mapping[str, Any]) -> Mapping[str, Any]:
        return {
            "device_id": raw.get("devId"),
            "name": raw.get("devName"),
            "station_code": raw.get("stationCode"),
            "type": raw.get("devTypeId"),
            "raw": dict(raw),
        }
