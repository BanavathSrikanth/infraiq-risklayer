from fastapi import FastAPI

from app.api.routes.risk_routes import router as risk_router

app = FastAPI(
    title="Risk Service API",
    description=(
        "Calculates Asset Health Score (AHS), Chronic Exposure Score (CES), "
        "Consequence Score (CQS), Dynamic Hazard Monitor (DHM), "
        "Vegetation Exposure Score (VES), and Operational Priority Score (OPS)."
    ),
)
app.include_router(risk_router)
