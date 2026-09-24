from typing import Any

from pydantic import BaseModel, Field

from ai.schemas import SourceReference


class AnalysisRequest(BaseModel):
    text: str = Field(min_length=1)
    source_references: list[SourceReference] = Field(default_factory=list)
    context: dict[str, Any] = Field(default_factory=dict)
