import json
from pathlib import Path

from app.domain.schemas.column_mapping import MappingRecord


class MappingStore:
    def __init__(self, path: str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def save(self, record: MappingRecord) -> MappingRecord:
        records = self._read()
        records[record.mapping_id] = record.model_dump(mode="json")
        self.path.write_text(json.dumps(records, indent=2), encoding="utf-8")
        return record

    def get(self, mapping_id: str) -> MappingRecord | None:
        payload = self._read().get(mapping_id)
        return MappingRecord.model_validate(payload) if payload else None

    def _read(self) -> dict:
        if not self.path.exists():
            return {}
        return json.loads(self.path.read_text(encoding="utf-8"))