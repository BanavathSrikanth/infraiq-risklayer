from __future__ import annotations

from typing import Annotated

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
import os
from libs.common.observability import CorrelationIdMiddleware

from app.domain.models import MappingSpec, PipelineResult, Source
from app.domain.pipeline import IntegrationPipeline
from app.infrastructure.blob import AzureBlobLandingAdapter, InMemoryBlobLandingAdapter
from app.infrastructure.repository import InMemoryIntegrationRepository

repository = InMemoryIntegrationRepository()
blob_connection_string = os.getenv("BLOB_CONNECTION_STRING")
blob = (
    AzureBlobLandingAdapter(
        blob_connection_string,
        os.getenv("BLOB_CONTAINER", "infraiq"),
    )
    if blob_connection_string
    else InMemoryBlobLandingAdapter()
)
pipeline = IntegrationPipeline(repository, blob)

app = FastAPI(title="Integration Source Data Service", version="1.0.0")
app.add_middleware(CorrelationIdMiddleware)


def get_repository() -> InMemoryIntegrationRepository:
    return repository


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy", "service": "integration-service"}


@app.post("/api/v1/sources", response_model=Source, status_code=201)
def register_source(source: Source, repo: Annotated[InMemoryIntegrationRepository, Depends(get_repository)]) -> Source:
    return repo.save(source)


@app.get("/api/v1/sources", response_model=list[Source])
def list_sources(tenant_id: str, repo: Annotated[InMemoryIntegrationRepository, Depends(get_repository)]) -> list[Source]:
    return repo.list(tenant_id)


@app.post("/api/v1/sources/{source_id}/ingest", response_model=PipelineResult)
async def ingest_source(
    source_id: str,
    tenant_id: Annotated[str, Form()],
    mapping_json: Annotated[str, Form()],
    file: UploadFile = File(...),
    repo: InMemoryIntegrationRepository = Depends(get_repository),
) -> PipelineResult:
    source = repo.get(source_id)
    if not isinstance(source, Source) or source.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Source not found")
    mapping = MappingSpec.model_validate_json(mapping_json)
    if mapping.source_id != source_id:
        raise HTTPException(status_code=400, detail="Mapping source_id does not match path")
    return pipeline.ingest(source, await file.read(), file.content_type or "text/csv", mapping)


@app.get("/api/v1/canonical", response_model=list)
def list_canonical(tenant_id: str, repo: Annotated[InMemoryIntegrationRepository, Depends(get_repository)]):
    return repo.list_canonical(tenant_id)
