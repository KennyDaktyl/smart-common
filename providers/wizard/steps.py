# smart_common/providers/wizard/steps.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Generic, Mapping, TypedDict, Type, TypeVar

from pydantic import BaseModel


WizardContext = Mapping[str, Any]


class WizardHandlerResult(TypedDict, total=False):
    next_step: str | None
    options: Mapping[str, Any]
    context: WizardContext
    session_updates: Mapping[str, Any]
    final_config: Mapping[str, Any]
    is_complete: bool


ModelType = TypeVar("ModelType", bound=BaseModel)


WizardHandler = Callable[[ModelType, Mapping[str, Any]], WizardHandlerResult]


@dataclass(frozen=True)
class WizardStep(Generic[ModelType]):
    """Definition of a single wizard step."""

    schema: Type[ModelType]
    handler: WizardHandler[ModelType]
