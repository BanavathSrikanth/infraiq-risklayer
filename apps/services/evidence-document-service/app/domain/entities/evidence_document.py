from dataclasses import dataclass


@dataclass
class EvidenceDocument:
    document_id: str
    asset_id: str
    tenant_id: str
    file_name: str
    url: str
    status: str = "uploaded"
