using System.ComponentModel.DataAnnotations;
using System.Text.Json.Serialization;

namespace RiskBff.Models;

public sealed class PolePriorityRequest
{
    [Required]
    [JsonPropertyName("asset_id")]
    public required string AssetId { get; init; }

    [Required]
    [JsonPropertyName("tenant_id")]
    public required string TenantId { get; init; }

    [Required]
    [JsonPropertyName("risk_evaluation_id")]
    public required string RiskEvaluationId { get; init; }

    [Range(0, 100)]
    [JsonPropertyName("risk_score")]
    public double RiskScore { get; init; }

    [Range(0, 100)]
    [JsonPropertyName("hazard_exposure")]
    public double HazardExposure { get; init; }

    [Range(0, 100)]
    [JsonPropertyName("consequence_score")]
    public double ConsequenceScore { get; init; }

    [Range(0, 100)]
    [JsonPropertyName("treatment_urgency")]
    public double TreatmentUrgency { get; init; }

    [Range(0, 100)]
    [JsonPropertyName("inspection_confidence")]
    public double InspectionConfidence { get; init; } = 100;
}