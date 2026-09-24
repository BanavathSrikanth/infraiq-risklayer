from app.application.column_mapping.profiler import profile_file
from app.config import Settings
from app.domain.schemas.column_mapping import MappingRecord, MappingProposal, ReviewMappingRequest
from app.infrastructure.providers.microsoft_foundry.column_mapper import AzureOpenAIColumnMapper
from app.infrastructure.storage.blob_client import SourceFileClient
from app.infrastructure.storage.mapping_store import MappingStore


class ColumnMappingService:
    def __init__(self, settings: Settings):
        self.sources = SourceFileClient(settings)
        self.mapper = AzureOpenAIColumnMapper(settings)
        self.store = MappingStore(settings.mapping_store_path)

    def propose(self, tenant_id: str, schema_name: str, source_uri: str, target_fields: list[str]) -> MappingRecord:
        filename, content = self.sources.read(source_uri)
        columns = profile_file(filename, content)
        proposal = self.mapper.propose(columns, target_fields)
        self._validate(proposal, columns, target_fields)
        record = MappingRecord(tenant_id=tenant_id, source_uri=source_uri, schema_name=schema_name, columns=columns, proposal=proposal)
        return self.store.save(record)

    def review(self, mapping_id: str, request: ReviewMappingRequest) -> MappingRecord:
        record = self.store.get(mapping_id)
        if record is None:
            raise KeyError(mapping_id)
        if request.mappings is not None:
            self._validate(MappingProposal(mappings=request.mappings), record.columns, [item.target_field for item in request.mappings if item.target_field])
            record.proposal.mappings = request.mappings
        record.status = request.decision
        record.reviewed_by = request.reviewer
        from datetime import datetime, timezone

        record.reviewed_at = datetime.now(timezone.utc)
        return self.store.save(record)

    @staticmethod
    def _validate(proposal: MappingProposal, columns, target_fields: list[str]):
        source_names = {column.name for column in columns}
        mapped_sources = [item.source_column for item in proposal.mappings]
        if any(source not in source_names for source in mapped_sources):
            raise ValueError("Mapping references a source column that does not exist")
        if len(mapped_sources) != len(set(mapped_sources)):
            raise ValueError("A source column may only be mapped once")
        if any(item.target_field not in target_fields for item in proposal.mappings):
            raise ValueError("Mapping references a target field outside the requested schema")
        proposal.requires_review = proposal.requires_review or any(item.confidence < 0.85 for item in proposal.mappings)