# smart-api/smart_common/schemas/pagination_schema.py
from __future__ import annotations

from typing import Generic, List, TypeVar

from pydantic import Field

from smart_common.schemas.base import APIModel

T = TypeVar("T")


class PaginationMeta(APIModel):
    total: int = Field(..., description="Total number of items")
    limit: int = Field(..., description="Max items per page")
    offset: int = Field(..., description="Offset from start")


class PaginatedResponse(APIModel, Generic[T]):
    meta: PaginationMeta
    items: List[T]


class PaginationQuery(APIModel):
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)
