from typing import Any

from fastapi import FastAPI
from libs.common.observability import CorrelationIdMiddleware

from app.api.routes import classification, column_mapping, evaluation, extraction, rag, relationship
from app.config import get_settings

settings = get_settings()
app = FastAPI(
    title="InfraIQ AI Orchestration Service",
    version="1.0.0",
    description=(
        "AI proposal orchestration. Outputs are non-authoritative and must be "
        "validated by application/domain services before persistence."
    ),
)
app.add_middleware(CorrelationIdMiddleware)

for router in (extraction.router, classification.router, relationship.router, rag.router, evaluation.router, column_mapping.router):
    app.include_router(router, prefix="/api/v1")


@app.get("/health", tags=["system"])
def health() -> dict[str, Any]:
    return {"status": "healthy", "service": settings.service_name}
