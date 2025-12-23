from __future__ import annotations

from typing import Any, List, Optional
from uuid import UUID

from sqlalchemy.orm import Query, joinedload

from smart_common.models.microcontroller import Microcontroller
from smart_common.repositories.base import BaseRepository


class MicrocontrollerRepository(BaseRepository[Microcontroller]):
    model = Microcontroller

    def get_by_uuid(self, uuid: UUID) -> Optional[Microcontroller]:
        return self.session.query(self.model).filter(self.model.uuid == uuid).first()

    def get_for_user(self, user_id: int) -> List[Microcontroller]:
        return (
            self.session.query(self.model).filter(self.model.user_id == user_id).all()
        )

    def get_for_user_by_uuid(
        self, uuid: UUID, user_id: int
    ) -> Optional[Microcontroller]:
        return (
            self.session.query(self.model)
            .filter(
                self.model.uuid == uuid,
                self.model.user_id == user_id,
            )
            .first()
        )

    def create(self, data: dict) -> Microcontroller:
        microcontroller = Microcontroller(**data)
        self.session.add(microcontroller)
        self.session.flush()
        self.session.commit()
        self.session.refresh(microcontroller)
        return microcontroller

    def update_for_user(
        self, uuid: UUID, user_id: int, data: dict
    ) -> Optional[Microcontroller]:
        microcontroller = self.get_for_user_by_uuid(uuid, user_id)
        if not microcontroller:
            return None
        for key, value in data.items():
            setattr(microcontroller, key, value)
        self.session.flush()
        self.session.refresh(microcontroller)
        return microcontroller

    def delete_for_user(self, uuid: UUID, user_id: int) -> bool:
        microcontroller = self.get_for_user_by_uuid(uuid, user_id)
        if not microcontroller:
            return False
        self.session.delete(microcontroller)
        self.session.flush()
        return True

    def get_full_for_user(self, user_id: int):
        microcontrollers = (
            self.session.query(self.model)
            .filter(self.model.user_id == user_id)
            .options(
                joinedload(self.model.devices),
                joinedload(self.model.sensor_providers),
                joinedload(self.model.power_provider),
                joinedload(self.model.sensor_capabilities),
            )
            .all()
        )
        return microcontrollers

    def _with_full_options(self, query: Query) -> Query:
        return query.options(
            joinedload(self.model.devices),
            joinedload(self.model.sensor_providers),
            joinedload(self.model.power_provider),
            joinedload(self.model.sensor_capabilities),
            joinedload(self.model.user),
        )

    def list_full(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        filters: dict[str, Any] | None = None,
        order_by: Any | None = None,
    ) -> list[Microcontroller]:
        query = self._with_full_options(self._base_query())
        query = self._apply_filters(query, filters)

        if order_by is not None:
            query = query.order_by(order_by)

        if offset is not None:
            query = query.offset(offset)

        if limit is not None:
            query = query.limit(limit)

        return query.all()

    def list_all_for_admin(self):
        return (
            self.session.query(self.model)
            .options(
                joinedload(self.model.user),
                joinedload(self.model.devices),
                joinedload(self.model.sensor_providers),
                joinedload(self.model.power_provider),
                joinedload(self.model.sensor_capabilities),
            )
            .all()
        )

    def get_full_by_uuid(self, uuid: UUID) -> Microcontroller | None:
        return (
            self.session.query(self.model)
            .filter(self.model.uuid == uuid)
            .options(
                joinedload(self.model.user),
                joinedload(self.model.devices),
                joinedload(self.model.sensor_providers),
                joinedload(self.model.power_provider),
                joinedload(self.model.sensor_capabilities),
            )
            .one_or_none()
        )
