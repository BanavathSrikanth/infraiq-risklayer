from fastapi import APIRouter, Depends, HTTPException

from app.application.services.evidence_service import EvidenceApplicationService
from app.infrastructure.repositories.evidence_repository import EvidenceRepository

router = APIRouter(prefix="/evidence", tags=["evidence"])


def get_evidence_service() -> EvidenceApplicationService:
    return EvidenceApplicationService(EvidenceRepository())


@router.post("")
async def upload_document(
    payload: dict,
    service: EvidenceApplicationService = Depends(get_evidence_service),
):
    try:
        document = service.upload_document(
            document_id=payload["document_id"],
            asset_id=payload["asset_id"],
            tenant_id=payload["tenant_id"],
            file_name=payload["file_name"],
            url=payload["url"],
        )
        return {
            "document_id": document.document_id,
            "asset_id": document.asset_id,
            "tenant_id": document.tenant_id,
            "file_name": document.file_name,
            "status": document.status,
            "url": document.url,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("")
async def list_documents(
    tenant_id: str,
    asset_id: str | None = None,
    service: EvidenceApplicationService = Depends(get_evidence_service),
):
    documents = service.list_documents(tenant_id, asset_id)
    return [
        {
            "document_id": item.document_id,
            "asset_id": item.asset_id,
            "tenant_id": item.tenant_id,
            "file_name": item.file_name,
            "status": item.status,
            "url": item.url,
        }
        for item in documents
    ]
