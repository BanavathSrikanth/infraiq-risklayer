from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List

from app.domain.entities.finding import Finding


@dataclass
class Inspection:
    inspection_id: str
    asset_id: str
    tenant_id: str
    findings: List[Finding] = field(default_factory=list)
    inspected_at: datetime | None = None

    def __post_init__(self):
        if self.inspected_at is None:
            self.inspected_at = datetime.now(timezone.utc)

    def add_finding(
        self,
        finding_id: str,
        finding_type: str,
        description: str,
        severity: str = "unknown",
    ) -> Finding:
        finding = Finding(
            finding_id=finding_id,
            asset_id=self.asset_id,
            tenant_id=self.tenant_id,
            inspection_id=self.inspection_id,
            finding_type=finding_type,
            description=description,
            severity=severity,
        )
        self.findings.append(finding)
        return finding
