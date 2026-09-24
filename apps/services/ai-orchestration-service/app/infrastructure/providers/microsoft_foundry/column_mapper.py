from app.config import Settings
from app.domain.schemas.column_mapping import ColumnProfile, MappingProposal


class AzureOpenAIColumnMapper:
    def __init__(self, settings: Settings):
        self.settings = settings

    def propose(self, columns: list[ColumnProfile], target_fields: list[str]) -> MappingProposal:
        if not self.settings.azure_openai_endpoint or not self.settings.azure_openai_api_key:
            return self._deterministic_proposal(columns, target_fields)

        from openai import AzureOpenAI

        client = AzureOpenAI(
            api_key=self.settings.azure_openai_api_key,
            azure_endpoint=self.settings.azure_openai_endpoint,
            api_version=self.settings.azure_openai_api_version,
        )
        response = client.beta.chat.completions.parse(
            model=self.settings.azure_openai_deployment,
            temperature=0,
            response_format=MappingProposal,
            messages=[
                {"role": "system", "content": "Map source columns to the target schema. Never invent source columns. Use null for unmapped targets."},
                {"role": "user", "content": str({"source_columns": [column.model_dump() for column in columns], "target_fields": target_fields})},
            ],
        )
        parsed = response.choices[0].message.parsed
        if parsed is None:
            raise ValueError("Azure OpenAI returned no structured mapping")
        return parsed

    @staticmethod
    def _deterministic_proposal(columns: list[ColumnProfile], target_fields: list[str]) -> MappingProposal:
        normalized = {column.name.lower().replace("_", "").replace(" ", ""): column.name for column in columns}
        mappings = []
        used = set()
        for target in target_fields:
            source = normalized.get(target.lower().replace("_", "").replace(" ", ""))
            if source:
                mappings.append({"source_column": source, "target_field": target, "confidence": 0.75, "transformation": None, "reason": "Normalized name match"})
                used.add(source)
        return MappingProposal(
            mappings=mappings,
            unmapped_columns=[column.name for column in columns if column.name not in used],
            requires_review=True,
        )