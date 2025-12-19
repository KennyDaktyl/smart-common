from __future__ import annotations

from smart_common.models.installation import Installation
from smart_common.repositories.base import BaseRepository


class InstallationRepository(BaseRepository[Installation]):
    model = Installation

    def list_by_user(self, user_id: int) -> list[Installation]:
        return (
            self.session.query(self.model)
            .filter(
                self.model.user_id == user_id,
                self.model.is_active.is_(True),
            )
            .all()
        )

    def get_by_id(self, installation_id: int) -> Installation | None:
        return self.session.get(self.model, installation_id)

    def exists_by_station_code(self, code: str) -> bool:
        return (
            self.session.query(self.model.id)
            .filter(
                self.model.station_code == code,
                self.model.is_active.is_(True),
            )
            .first()
            is not None
        )

    def soft_delete(self, installation: Installation) -> None:
        installation.is_active = False
        self.session.add(installation)

    def get_active_for_user(
        self,
        installation_id: int,
        user_id: int,
    ) -> Installation | None:
        return (
            self.session.query(self.model)
            .filter(
                self.model.id == installation_id,
                self.model.user_id == user_id,
                self.model.is_active.is_(True),
            )
            .one_or_none()
        )
