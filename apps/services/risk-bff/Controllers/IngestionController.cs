using Microsoft.AspNetCore.Mvc;
using RiskBff.Models;
using RiskBff.Services;

namespace RiskBff.Controllers;

[ApiController]
[Route("api/v1/ingestion")]
[Produces("application/json")]
public class IngestionController(IBlobPreviewService previewService, ILogger<IngestionController> logger) : ControllerBase
{
    /// <summary>
    /// Retrieves paginated, filterable, and searchable preview data for uploaded asset files.
    /// Data is fetched and parsed from Azure Blob Storage or staged upload state.
    /// </summary>
    /// <param name="queryParams">Paging, filtering, sorting, and blob/upload parameters.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Preview file summary, validation metrics, and paginated records.</returns>
    [HttpGet("preview")]
    [ProducesResponseType(typeof(DataPreviewResponse), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<DataPreviewResponse>> GetPreview(
        [FromQuery] DataPreviewQueryParams queryParams,
        CancellationToken cancellationToken)
    {
        try
        {
            var tenantId = User.FindFirst("tenant_id")?.Value
                ?? Request.Headers["X-Tenant-Id"].FirstOrDefault()
                ?? queryParams.TenantId
                ?? "tenant-demo";

            queryParams.TenantId = tenantId;

            var response = await previewService.GetPreviewAsync(queryParams, cancellationToken);
            return Ok(response);
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "Error generating ingestion preview for blob '{BlobName}'", queryParams.BlobName ?? queryParams.UploadId);
            return StatusCode(StatusCodes.Status500InternalServerError, new { error = "Failed to load data preview", detail = ex.Message });
        }
    }

    /// <summary>
    /// Retrieves preview data by a specific upload identifier or blob name in the route.
    /// </summary>
    /// <param name="uploadId">Upload identifier or blob path.</param>
    /// <param name="queryParams">Paging, filtering, and sorting parameters.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    [HttpGet("uploads/{uploadId}/preview")]
    [ProducesResponseType(typeof(DataPreviewResponse), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<DataPreviewResponse>> GetPreviewByUploadId(
        [FromRoute] string uploadId,
        [FromQuery] DataPreviewQueryParams queryParams,
        CancellationToken cancellationToken)
    {
        queryParams.UploadId = uploadId;
        return await GetPreview(queryParams, cancellationToken);
    }
}
