using System.Text.Json;
using Microsoft.AspNetCore.Mvc;
using RiskBff.Clients;
using RiskBff.Models;

namespace RiskBff.Controllers;

[ApiController]
[Route("api/v1/risks")]
public class RiskController(IRiskServiceClient riskServiceClient) : ControllerBase
{
    [HttpPost("ingest/blob")]
    public async Task<IActionResult> IngestBlob([FromBody] RiskIngestRequest request, CancellationToken cancellationToken)
    {
        // Extract tenant_id from claims in a real scenario
        // request.TenantId = User.FindFirst("tenant_id")?.Value;

        var response = await riskServiceClient.IngestBlobAsync(request, cancellationToken);
        if (response == null)
        {
            return StatusCode(StatusCodes.Status500InternalServerError, "Failed to parse response from downstream service.");
        }

        return Ok(response);
    }

    [HttpPost("calculate")]
    public async Task<IActionResult> CalculateRisk([FromBody] JsonElement request, CancellationToken cancellationToken)
    {
        // Extract tenant_id from claims in a real scenario
        // if (request.TryGetProperty("tenant_id", out var tenantId)) { ... }

        var response = await riskServiceClient.CalculateRiskAsync(request, cancellationToken);
        if (response == null)
        {
            return StatusCode(StatusCodes.Status500InternalServerError, "Failed to parse response from downstream service.");
        }

        return Ok(response.Value);
    }

    [HttpGet("latest/{assetId}")]
    public async Task<IActionResult> LatestRisk(
        [FromRoute] string assetId,
        [FromQuery(Name = "tenant_id")] string tenantId,
        CancellationToken cancellationToken)
    {
        using var response = await riskServiceClient.GetLatestRiskAsync(assetId, tenantId, cancellationToken);
        return await ForwardResponseAsync(response, cancellationToken);
    }

    [HttpPost("pole-priority")]
    public async Task<IActionResult> CalculatePolePriority(
        [FromBody] PolePriorityRequest request,
        CancellationToken cancellationToken)
    {
        using var response = await riskServiceClient.CalculatePolePriorityAsync(request, cancellationToken);
        return await ForwardResponseAsync(response, cancellationToken);
    }

    [HttpGet("history/{assetId}")]
    public async Task<IActionResult> RiskHistory(
        [FromRoute] string assetId,
        [FromQuery(Name = "tenant_id")] string tenantId,
        CancellationToken cancellationToken)
    {
        using var response = await riskServiceClient.GetRiskHistoryAsync(assetId, tenantId, cancellationToken);
        return await ForwardResponseAsync(response, cancellationToken);
    }

    private static async Task<IActionResult> ForwardResponseAsync(
        HttpResponseMessage response,
        CancellationToken cancellationToken)
    {
        var content = await response.Content.ReadAsStringAsync(cancellationToken);
        return new ContentResult
        {
            Content = content,
            ContentType = response.Content.Headers.ContentType?.ToString() ?? "application/json",
            StatusCode = (int)response.StatusCode
        };
    }
}
