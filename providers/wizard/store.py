# smart_common/providers/wizard/store.py
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from threading import Lock
from typing import Any, Dict
from uuid import uuid4

from smart_common.providers.enums import ProviderVendor


@dataclass
class WizardSession:
    id: str
    vendor: ProviderVendor
    session_data: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    last_step: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


class WizardSessionStore:
    """In-memory store that keeps wizard state between requests."""

    def __init__(self, ttl_seconds: int = 600):
        self._sessions: Dict[str, WizardSession] = {}
        self._lock = Lock()
        self._ttl = timedelta(seconds=ttl_seconds)

    def create(self, vendor: ProviderVendor) -> WizardSession:
        with self._lock:
            session_id = uuid4().hex
            session = WizardSession(
                id=session_id,
                vendor=vendor,
                context={"wizard_session_id": session_id},
            )
            self._sessions[session_id] = session
            return session

    def get(self, session_id: str) -> WizardSession | None:
        with self._lock:
            self._cleanup()
            session = self._sessions.get(session_id)
            if not session:
                return None
            session.updated_at = datetime.utcnow()
            return session

    def persist(self, session: WizardSession) -> None:
        with self._lock:
            session.updated_at = datetime.utcnow()
            self._sessions[session.id] = session

    def delete(self, session_id: str) -> None:
        with self._lock:
            self._sessions.pop(session_id, None)

    def _cleanup(self) -> None:
        now = datetime.utcnow()
        expired = [
            session_id
            for session_id, session in self._sessions.items()
            if now - session.updated_at > self._ttl
        ]
        for session_id in expired:
            self._sessions.pop(session_id, None)
