from fastapi import APIRouter, Depends, HTTPException

from app.application.column_mapping.service import ColumnMappingService
from app.config import Settings, get_settings
from app.domain.schemas.column_mapping import CreateMappingRequest, MappingRecord, ReviewMappingRequest

router = APIRouter(prefix="/column-mappings", tags=["column-mappings"])


def get_service(settings: Settings = Depends(get_settings)) -> ColumnMappingService:
    return ColumnMappingService(settings)


@router.post("/propose", response_model=MappingRecord)
def propose(request: CreateMappingRequest, service: ColumnMappingService = Depends(get_service)):
    try:
        return service.propose(**request.model_dump())
    except (OSError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.post("/{mapping_id}/review", response_model=MappingRecord)
def review(mapping_id: str, request: ReviewMappingRequest, service: ColumnMappingService = Depends(get_service)):
    try:
        return service.review(mapping_id, request)
    except KeyError as error:
        raise HTTPException(status_code=404, detail="Mapping proposal not found") from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error