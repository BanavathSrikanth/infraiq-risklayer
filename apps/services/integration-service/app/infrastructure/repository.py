from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from app.domain.models import (
    CanonicalRecord,
    LandingObject,
    MappingSpec,
    Profile,
    Provenance,
    Source,
)

T = TypeVar("T")


class Repository(ABC, Generic[T]):
    @abstractmethod
    def save(self, value: T) -> T: ...


class SourceRepository(Repository[Source], ABC):
    @abstractmethod
    def get(self, source_id: str) -> Source | None: ...

    @abstractmethod
    def list(self, tenant_id: str) -> list[Source]: ...


class LandingRepository(Repository[LandingObject], ABC):
    @abstractmethod
    def get(self, landing_id: str) -> LandingObject | None: ...


class IntegrationRepository(SourceRepository, LandingRepository, ABC):
    @abstractmethod
    def save_profile(self, profile: Profile) -> Profile: ...

    @abstractmethod
    def save_mapping(self, mapping: MappingSpec) -> MappingSpec: ...

    @abstractmethod
    def save_canonical(self, record: CanonicalRecord) -> CanonicalRecord: ...

    @abstractmethod
    def save_provenance(self, provenance: Provenance) -> Provenance: ...

    @abstractmethod
    def list_canonical(self, tenant_id: str) -> list[CanonicalRecord]: ...


class InMemoryIntegrationRepository(IntegrationRepository):
    """Deterministic adapter for local development and contract tests."""

    def __init__(self) -> None:
        self.sources: dict[str, Source] = {}
        self.landings: dict[str, LandingObject] = {}
        self.profiles: dict[str, Profile] = {}
        self.mappings: dict[str, MappingSpec] = {}
        self.canonical: dict[str, CanonicalRecord] = {}
        self.provenance: dict[str, Provenance] = {}

    def save(self, value: T) -> T:
        if isinstance(value, Source):
            self.sources[value.id] = value
        elif isinstance(value, LandingObject):
            self.landings[value.id] = value
        else:
            raise TypeError(f"Unsupported repository value: {type(value)!r}")
        return value

    def get(self, entity_id: str):
        return self.sources.get(entity_id) or self.landings.get(entity_id)

    def list(self, tenant_id: str) -> list[Source]:
        return [s for s in self.sources.values() if s.tenant_id == tenant_id]

    def save_profile(self, profile: Profile) -> Profile:
        self.profiles[profile.landing_id] = profile
        return profile

    def save_mapping(self, mapping: MappingSpec) -> MappingSpec:
        self.mappings[mapping.source_id] = mapping
        return mapping

    def save_canonical(self, record: CanonicalRecord) -> CanonicalRecord:
        self.canonical[record.record_id] = record
        return record

    def save_provenance(self, provenance: Provenance) -> Provenance:
        self.provenance[provenance.id] = provenance
        return provenance

    def list_canonical(self, tenant_id: str) -> list[CanonicalRecord]:
        return [r for r in self.canonical.values() if r.tenant_id == tenant_id]
