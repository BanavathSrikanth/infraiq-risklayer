from fastapi import FastAPI

from app.api import router
from libs.common.observability import CorrelationIdMiddleware

app = FastAPI(title="InfraIQ Geospatial Service", version="1.0.0")
app.add_middleware(CorrelationIdMiddleware)
app.include_router(router)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "healthy", "service": "geospatial"}
