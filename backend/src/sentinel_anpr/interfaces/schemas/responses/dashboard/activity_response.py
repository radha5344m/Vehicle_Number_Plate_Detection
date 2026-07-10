"""Recent activity response schema."""

from datetime import datetime

from pydantic import BaseModel


class RecentActivityItemData(BaseModel):
    """Single activity row."""

    id: str
    plate_text: str
    activity_type: str
    description: str
    status: str
    occurred_at: datetime


class RecentActivityData(BaseModel):
    """Recent activity list payload."""

    items: list[RecentActivityItemData]
