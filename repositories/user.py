from __future__ import annotations

from typing import Any, Optional

from sqlalchemy.orm import selectinload

from smart_common.models.microcontroller import Microcontroller
from smart_common.models.user import User
from smart_common.models.user_profile import UserProfile
from smart_common.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    ADMIN_EDITABLE_FIELDS = {"email", "role", "is_active"}
    SELF_EDITABLE_FIELDS = {"email"}

    searchable_fields = {
        "email": User.email,
        "is_active": User.is_active,
        "role": User.role,
    }

    # -----------------------------
    # BASIC
    # -----------------------------
    def get_by_email(self, email: str) -> Optional[User]:
        return self.session.query(User).filter(User.email == email).first()

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.session.get(User, user_id)

    # -----------------------------
    # AUTH / STATE
    # -----------------------------
    def activate_user(self, user: User) -> User:
        """
        Activate user after email confirmation.
        """
        user.is_active = True
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def deactivate_user(self, user: User) -> User:
        return self.partial_update(
            user,
            data={"is_active": False},
            allowed_fields={"is_active"},
        )

    def update_password(self, user: User, password_hash: str) -> User:
        user.password_hash = password_hash
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    # -----------------------------
    # MICROCONTROLLERS (średnie)
    # -----------------------------
    def get_with_microcontrollers(self, user_id: int) -> Optional[User]:
        return (
            self.session.query(User)
            .options(selectinload(User.microcontrollers))
            .filter(User.id == user_id)
            .first()
        )

    # -----------------------------
    # FULL DETAILS (ciężkie)
    # -----------------------------
    def get_with_microcontrollers_details(self, user_id: int) -> Optional[User]:
        return (
            self.session.query(User)
            .options(
                selectinload(User.microcontrollers).selectinload(
                    Microcontroller.devices
                ),
                selectinload(User.microcontrollers).selectinload(
                    Microcontroller.sensor_providers
                ),
                selectinload(User.microcontrollers).selectinload(
                    Microcontroller.power_provider
                ),
            )
            .filter(User.id == user_id)
            .first()
        )

    def get_with_profile(self, user_id: int) -> Optional[User]:
        return (
            self.session.query(User)
            .outerjoin(User.profile)
            .filter(User.id == user_id)
            .first()
        )

    # -----------------------------
    # PROFILE
    # -----------------------------
    def upsert_profile(
        self,
        user: User,
        data: dict,
    ) -> UserProfile:
        if user.profile is None:
            user.profile = UserProfile(
                user_id=user.id,
                **data,
            )
        else:
            for key, value in data.items():
                setattr(user.profile, key, value)

        self.session.add(user.profile)
        self.session.commit()
        self.session.refresh(user.profile)
        return user.profile

    # -----------------------------
    # PARTIAL UPDATES
    # -----------------------------
    def update_user_admin(
        self,
        user: User,
        data: dict[str, Any],
    ) -> User:
        return self.partial_update(
            user,
            data=data,
            allowed_fields=self.ADMIN_EDITABLE_FIELDS,
        )

    def update_user_self(
        self,
        user: User,
        data: dict[str, Any],
    ) -> User:
        return self.partial_update(
            user,
            data=data,
            allowed_fields=self.SELF_EDITABLE_FIELDS,
        )
