"""Versioned event contracts and an idempotent event envelope."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4


EventType = Literal[
    "inspection.submitted",
    "risk.evaluation_completed",
    "vegetation.imported",
    "vegetation.exposure_calculated",
    "decision.approved",
    "work.completed",
    "verification.completed",
    "risk.residual_evaluation_requested",
]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class DomainEvent:
    event_type: EventType
    tenant_id: str
    aggregate_id: str
    payload: dict[str, Any]
    event_id: str = field(default_factory=lambda: str(uuid4()))
    event_version: str = "1.0"
    occurred_at: datetime = field(default_factory=utc_now)
    correlation_id: str = field(default_factory=lambda: str(uuid4()))
    causation_id: str | None = None
    idempotency_key: str = ""

    def __post_init__(self) -> None:
        if not self.tenant_id.strip():
            raise ValueError("tenant_id is required")
        if not self.aggregate_id.strip():
            raise ValueError("aggregate_id is required")
        if not self.idempotency_key:
            object.__setattr__(self, "idempotency_key", self.event_id)


class InMemoryEventBus:
    """Test adapter; production deployments should bind this contract to a broker."""

    def __init__(self) -> None:
        self._events: list[DomainEvent] = []
        self._keys: set[tuple[str, str]] = set()

    def publish(self, event: DomainEvent) -> bool:
        key = (event.tenant_id, event.idempotency_key)
        if key in self._keys:
            return False
        self._keys.add(key)
        self._events.append(event)
        return True

    def events(self, tenant_id: str) -> list[DomainEvent]:
        return [event for event in self._events if event.tenant_id == tenant_id]
