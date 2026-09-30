using Microsoft.AspNetCore.Mvc;
using Microsoft.VisualBasic.FileIO;
using Npgsql;
using RiskBff.Models;
using RiskBff.Repositories;
using RiskBff.Services;

namespace RiskBff.Controllers;

[ApiController]
[Route("api/v1/imports")]
public sealed class ImportPreviewController(
    ImportPreviewRepository repository,
    CsvImportPreviewReader previewReader,
    IConfiguration configuration,
    IWebHostEnvironment environment) : ControllerBase
{
    [HttpGet("{importId}/preview")]
    [ProducesResponseType<ImportPreviewResponse>(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status413PayloadTooLarge)]
    [ProducesResponseType(StatusCodes.Status415UnsupportedMediaType)]
    [ProducesResponseType(StatusCodes.Status503ServiceUnavailable)]
    public async Task<ActionResult<ImportPreviewResponse>> GetPreview(
        [FromRoute] string importId,
        [FromQuery(Name = "tenant_id")] string tenantId,
        [FromQuery] int page = 1,
        [FromQuery(Name = "page_size")] int pageSize = 10,
        [FromQuery] string? search = null,
        [FromQuery(Name = "ingestion_status")] string? ingestionStatus = null,
        CancellationToken cancellationToken = default)
    {
        if (!Guid.TryParseExact(importId, "N", out _))
        {
            return NotFound();
        }

        if (string.IsNullOrWhiteSpace(tenantId))
        {
            return BadRequest(new { detail = "tenant_id is required" });
        }

        if (!repository.IsConfigured)
        {
            return StatusCode(StatusCodes.Status503ServiceUnavailable,
                new { detail = "Import storage is not configured" });
        }

        page = Math.Max(page, 1);
        pageSize = Math.Clamp(pageSize, 1, 100);

        var upload = await repository.GetForTenantAsync(importId, tenantId, cancellationToken);
        if (upload is null)
        {
            return NotFound();
        }

        if (!Path.GetExtension(upload.FileName).Equals(".csv", StringComparison.OrdinalIgnoreCase))
        {
            return StatusCode(StatusCodes.Status415UnsupportedMediaType,
                new { detail = "Preview currently supports CSV imports" });
        }

        var uploadDirectory = configuration["EvidenceUploadDirectory"];
        uploadDirectory = string.IsNullOrWhiteSpace(uploadDirectory)
            ? Path.Combine(environment.ContentRootPath, "uploads", "evidence")
            : Path.IsPathRooted(uploadDirectory)
                ? uploadDirectory
                : Path.Combine(environment.ContentRootPath, uploadDirectory);

        var storedFileName = Path.GetFileName(upload.StoredFileName);
        var storedPath = Path.Combine(uploadDirectory, storedFileName);
        if (!System.IO.File.Exists(storedPath))
        {
            return NotFound();
        }

        try
        {
            var preview = previewReader.ReadPage(
                storedPath,
                page,
                pageSize,
                search,
                ingestionStatus,
                cancellationToken);
            return Ok(new ImportPreviewResponse(
                upload.ImportId,
                upload.TenantId,
                upload.FileName,
                upload.UploadedOn,
                upload.UploadedBy,
                new ImportDataPreview(
                    preview.Columns,
                    preview.Rows,
                    page,
                    pageSize,
                    preview.TotalRecords,
                    preview.TotalMatchingRecords)));
        }
        catch (MalformedLineException)
        {
            return BadRequest(new { detail = "The CSV contains a malformed row" });
        }
        catch (InvalidDataException exception)
        {
            return BadRequest(new { detail = exception.Message });
        }
        catch (NpgsqlException)
        {
            return StatusCode(StatusCodes.Status503ServiceUnavailable,
                new { detail = "Import storage is unavailable" });
        }
    }
}