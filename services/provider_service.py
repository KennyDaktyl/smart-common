from typing import Callable
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from smart_common.models.provider import Provider
from smart_common.providers.enums import ProviderVendor
# ---- provider config schemas ----
from smart_common.providers.provider_config.huawei import HuaweiProviderConfig
from smart_common.repositories.microcontroller import MicrocontrollerRepository
from smart_common.repositories.provider import ProviderRepository


class ProviderService:
    def __init__(
        self,
        provider_repo_factory: Callable[[Session], ProviderRepository],
        microcontroller_repo_factory: Callable[[Session], MicrocontrollerRepository],
    ):
        self._provider_repo_factory = provider_repo_factory
        self._microcontroller_repo_factory = microcontroller_repo_factory

    # ---------- repositories ----------

    def _repo(self, db: Session) -> ProviderRepository:
        return self._provider_repo_factory(db)

    def _microcontroller_repo(self, db: Session) -> MicrocontrollerRepository:
        return self._microcontroller_repo_factory(db)

    # ---------- guards ----------

    def _ensure_microcontroller(self, db: Session, user_id: int, mc_uuid: UUID) -> int:
        microcontroller = self._microcontroller_repo(db).get_for_user_by_uuid(mc_uuid, user_id)
        if not microcontroller:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Microcontroller not found",
            )
        return microcontroller.id

    def _ensure_provider(self, db: Session, user_id: int, provider_id: int) -> Provider:
        provider = self._repo(db).get_for_user(provider_id, user_id)
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Provider not found",
            )
        return provider

    # ---------- CONFIG VALIDATION (TU JEST KLUCZ) ----------

    def _validate_config(self, vendor: ProviderVendor | str | None, config: dict) -> dict:
        if vendor is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Provider vendor is required",
            )

        try:
            vendor_enum = ProviderVendor(vendor)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid provider vendor: {vendor}",
            )

        if vendor_enum == ProviderVendor.HUAWEI:
            return HuaweiProviderConfig(**config).model_dump()

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unsupported provider vendor: {vendor_enum}",
        )

    # ---------- queries ----------

    def list_for_microcontroller(
        self,
        db: Session,
        user_id: int,
        mc_uuid: UUID,
    ) -> list[Provider]:
        microcontroller_id = self._ensure_microcontroller(db, user_id, mc_uuid)
        return db.query(Provider).filter(Provider.microcontroller_id == microcontroller_id).all()

    # ---------- commands ----------

    def create(
        self,
        db: Session,
        user_id: int,
        mc_uuid: UUID,
        payload: dict,
    ) -> Provider:
        microcontroller_id = self._ensure_microcontroller(db, user_id, mc_uuid)

        value_min = payload.get("value_min")
        value_max = payload.get("value_max")

        if value_min is None or value_max is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Both value_min and value_max must be provided",
            )

        if value_min >= value_max:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="value_min must be lower than value_max",
            )

        payload["config"] = self._validate_config(
            payload.get("vendor"),
            payload.get("config") or {},
        )

        provider = Provider(
            microcontroller_id=microcontroller_id,
            **payload,
        )

        self._repo(db).create(provider)
        db.commit()
        db.refresh(provider)
        return provider

    def update(
        self,
        db: Session,
        user_id: int,
        provider_id: int,
        payload: dict,
    ) -> Provider:
        provider = self._ensure_provider(db, user_id, provider_id)

        allowed_fields = {
            "name",
            "unit",
            "value_min",
            "value_max",
            "enabled",
            "config",
        }

        changes = {k: v for k, v in payload.items() if k in allowed_fields and v is not None}

        if not changes:
            return provider

        if "value_min" in changes or "value_max" in changes:
            new_min = changes.get("value_min", provider.value_min)
            new_max = changes.get("value_max", provider.value_max)

            if new_min >= new_max:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="value_min must be lower than value_max",
                )

        if "config" in changes:
            changes["config"] = self._validate_config(
                provider.vendor,
                changes["config"],
            )

        for attr, value in changes.items():
            setattr(provider, attr, value)

        db.commit()
        db.refresh(provider)
        return provider

    def set_enabled(
        self,
        db: Session,
        user_id: int,
        provider_id: int,
        enabled: bool,
    ) -> Provider:
        provider = self._ensure_provider(db, user_id, provider_id)
        provider.enabled = enabled
        db.commit()
        db.refresh(provider)
        return provider

    def get_provider(
        self,
        db: Session,
        user_id: int,
        provider_id: int,
    ) -> Provider:
        return self._ensure_provider(db, user_id, provider_id)
