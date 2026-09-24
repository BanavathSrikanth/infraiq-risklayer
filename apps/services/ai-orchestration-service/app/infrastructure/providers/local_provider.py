from ai.schemas import (
    AIProposalResponse,
    EntityProposal,
    ProvenanceMetadata,
    RecommendationProposal,
    RelationshipProposal,
)
from app.domain.schemas import AnalysisRequest


class LocalProposalProvider:
    """Offline provider used for development and contract tests.

    It emits proposals only; it never persists or mutates application records.
    """

    def __init__(
        self,
        provider_name: str = "local-deterministic",
        model_name: str = "proposal-engine",
        model_version: str = "1.0",
    ):
        self.provider_name = provider_name
        self.model_name = model_name
        self.model_version = model_version

    def _provenance(self, request: AnalysisRequest, operation: str, confidence: float) -> ProvenanceMetadata:
        return ProvenanceMetadata(
            model_provider=self.provider_name,
            model_name=self.model_name,
            model_version=self.model_version,
            prompt_id=f"{operation}.default",
            prompt_version="1.0",
            source_references=request.source_references,
            confidence=confidence,
        )

    def analyze(self, operation: str, request: AnalysisRequest) -> AIProposalResponse:
        provenance = self._provenance(request, operation, 0.55)
        entities: list[EntityProposal] = []
        relationships: list[RelationshipProposal] = []
        recommendations: list[RecommendationProposal] = []

        if operation in {"extraction", "classification"}:
            entities.append(
                EntityProposal(
                    entity_type="finding",
                    attributes={"text": request.text, "classification": operation},
                    provenance=provenance,
                )
            )
        if operation in {"relationship", "rag"}:
            relationships.append(
                RelationshipProposal(
                    relationship_type="requires_review",
                    source_entity=request.context.get("source_entity", "unknown"),
                    target_entity=request.context.get("target_entity", "unknown"),
                    provenance=provenance,
                )
            )
        if operation in {"recommendation", "evaluation"}:
            recommendations.append(
                RecommendationProposal(
                    recommendation_type="human_review",
                    rationale="AI output requires application/domain validation before it becomes authoritative.",
                    priority="medium",
                    provenance=provenance,
                )
            )

        return AIProposalResponse(
            operation=operation,
            entities=entities,
            relationships=relationships,
            recommendations=recommendations,
        )
