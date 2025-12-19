from typing import Callable

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from smart_common.models.installation import Installation
from smart_common.repositories.installation import InstallationRepository


class InstallationService:
    def __init__(self, repo_factory: Callable[[Session], InstallationRepository]):
        self._repo_factory = repo_factory

    def _repo(self, db: Session) -> InstallationRepository:
        return self._repo_factory(db)

    # -------------------------
    # READ
    # -------------------------

    def list_for_user(self, db: Session, user_id: int) -> list[Installation]:
        return self._repo(db).list_by_user(user_id)

    def get_for_user(
        self,
        db: Session,
        installation_id: int,
        user_id: int,
    ) -> Installation:
        installation = self._repo(db).get_active_for_user(
            installation_id=installation_id,
            user_id=user_id,
        )

        if not installation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Installation not found",
            )

        return installation

    # -------------------------
    # CREATE
    # -------------------------

    def create_for_user(
        self,
        db: Session,
        user_id: int,
        payload: dict,
    ) -> Installation:
        installation = Installation(
            user_id=user_id,
            is_active=True,
            **payload,
        )

        try:
            self._repo(db).create(installation)
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Installation with this station code already exists",
            )

        db.refresh(installation)
        return installation

    # -------------------------
    # UPDATE
    # -------------------------

    def update_for_user(
        self,
        db: Session,
        installation_id: int,
        user_id: int,
        payload: dict,
    ) -> Installation:
        repo = self._repo(db)

        installation = repo.get_active_for_user(
            installation_id=installation_id,
            user_id=user_id,
        )
        if not installation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Installation not found",
            )

        for key, value in payload.items():
            setattr(installation, key, value)

        db.commit()
        db.refresh(installation)
        return installation

    # -------------------------
    # DELETE (SOFT)
    # -------------------------

    def delete_for_user(
        self,
        db: Session,
        installation_id: int,
        user_id: int,
    ) -> None:
        repo = self._repo(db)

        installation = repo.get_active_for_user(
            installation_id=installation_id,
            user_id=user_id,
        )
        if not installation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Installation not found",
            )

        repo.soft_delete(installation)
        db.commit()
