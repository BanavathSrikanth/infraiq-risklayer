from common.events import DomainEvent, InMemoryEventBus


def test_event_bus_deduplicates_by_tenant_and_idempotency_key() -> None:
    bus = InMemoryEventBus()
    first = DomainEvent(
        event_type="inspection.submitted",
        tenant_id="tenant-a",
        aggregate_id="inspection-1",
        payload={"asset_id": "asset-1"},
        idempotency_key="client-event-1",
    )
    duplicate = DomainEvent(
        event_type="inspection.submitted",
        tenant_id="tenant-a",
        aggregate_id="inspection-1",
        payload={"asset_id": "asset-1"},
        idempotency_key="client-event-1",
    )

    assert bus.publish(first)
    assert not bus.publish(duplicate)
    assert len(bus.events("tenant-a")) == 1
