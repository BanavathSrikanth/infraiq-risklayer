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
}
