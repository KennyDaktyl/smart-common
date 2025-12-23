from __future__ import annotations

from typing import Optional

from smart_common.models.provider import ProviderCredential
from smart_common.repositories.base import BaseRepository


class ProviderCredentialRepository(BaseRepository[ProviderCredential]):
    model = ProviderCredential

    def get_by_provider_id(
        self,
        provider_id: int,
    ) -> Optional[ProviderCredential]:
        return (
            self.session.query(self.model)
            .filter(self.model.provider_id == provider_id)
            .one_or_none()
        )

    def delete_by_provider_id(self, provider_id: int) -> None:
        self.session.query(self.model).filter(
            self.model.provider_id == provider_id
        ).delete()
