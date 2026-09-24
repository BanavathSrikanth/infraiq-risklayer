from app.domain.entities.evidence_document import EvidenceDocument
from app.infrastructure.repositories.evidence_repository import EvidenceRepository


class EvidenceApplicationService:
    def __init__(self, repository: EvidenceRepository):
        self.repository = repository

    def upload_document(
        self,
        document_id: str,
        asset_id: str,
        tenant_id: str,
        file_name: str,
        url: str,
    ) -> EvidenceDocument:
        document = EvidenceDocument(
            document_id=document_id,
            asset_id=asset_id,
            tenant_id=tenant_id,
            file_name=file_name,
            url=url,
            status="uploaded",
        )
        return self.repository.save(document)

    def list_documents(self, tenant_id: str, asset_id: str | None = None) -> list[EvidenceDocument]:
        return self.repository.list_by_tenant(tenant_id, asset_id)
