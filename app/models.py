from typing import Literal

from pydantic import BaseModel, Field


class MonitorRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=128)
    step: int = Field(ge=0)
    content: str = Field(min_length=1, max_length=50_000)
    tool_name: str | None = Field(default=None, max_length=128)


class Signal(BaseModel):
    category: str
    score: float = Field(ge=0.0, le=1.0)
    reason: str


class MonitorResponse(BaseModel):
    session_id: str
    step: int
    decision: Literal["allow", "review", "block"]
    risk_score: float = Field(ge=0.0, le=1.0)
    signals: list[Signal]
