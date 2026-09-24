from typing import Dict, List, Optional

from app.domain.entities.evidence_document import EvidenceDocument


class EvidenceRepository:
    def __init__(self):
        self._store: Dict[str, EvidenceDocument] = {}

    def save(self, document: EvidenceDocument) -> EvidenceDocument:
        self._store[document.document_id] = document
        return document

    def get_by_id(self, document_id: str) -> Optional[EvidenceDocument]:
        return self._store.get(document_id)

    def list_by_tenant(self, tenant_id: str, asset_id: str | None = None) -> List[EvidenceDocument]:
        documents = [item for item in self._store.values() if item.tenant_id == tenant_id]
        if asset_id:
            documents = [item for item in documents if item.asset_id == asset_id]
        return documents
