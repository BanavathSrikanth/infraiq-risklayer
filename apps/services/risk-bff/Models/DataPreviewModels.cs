using System.Text.Json.Serialization;

namespace RiskBff.Models;

public class DataPreviewQueryParams
{
    [JsonPropertyName("blobName")]
    public string? BlobName { get; set; }

    [JsonPropertyName("uploadId")]
    public string? UploadId { get; set; }

    [JsonPropertyName("tenantId")]
    public string? TenantId { get; set; }

    [JsonPropertyName("page")]
    public int Page { get; set; } = 1;

    [JsonPropertyName("pageSize")]
    public int PageSize { get; set; } = 10;

    [JsonPropertyName("search")]
    public string? Search { get; set; }

    [JsonPropertyName("status")]
    public string? Status { get; set; }

    [JsonPropertyName("source")]
    public string? Source { get; set; }

    [JsonPropertyName("validationStatus")]
    public string? ValidationStatus { get; set; }

    [JsonPropertyName("sortBy")]
    public string? SortBy { get; set; } = "poleId";

    [JsonPropertyName("sortDirection")]
    public string? SortDirection { get; set; } = "asc";
}

public class PreviewFileInfo
{
    [JsonPropertyName("uploadId")]
    public string UploadId { get; set; } = string.Empty;

    [JsonPropertyName("tenantId")]
    public string TenantId { get; set; } = string.Empty;

    [JsonPropertyName("blobUri")]
    public string? BlobUri { get; set; }

    [JsonPropertyName("fileName")]
    public string FileName { get; set; } = string.Empty;

    [JsonPropertyName("uploadedAt")]
    public string UploadedAt { get; set; } = string.Empty;

    [JsonPropertyName("uploadedBy")]
    public string UploadedBy { get; set; } = string.Empty;

    [JsonPropertyName("fileSizeBytes")]
    public long FileSizeBytes { get; set; }

    [JsonPropertyName("fileSizeFormatted")]
    public string FileSizeFormatted { get; set; } = string.Empty;

    [JsonPropertyName("processingStatus")]
    public string ProcessingStatus { get; set; } = string.Empty;

    [JsonPropertyName("processingDuration")]
    public string ProcessingDuration { get; set; } = string.Empty;

    [JsonPropertyName("infoMessage")]
    public string InfoMessage { get; set; } = "This is a preview and validation step only. No assets are created yet. Fix issues and continue to map fields.";
}

public class PreviewSummary
{
    [JsonPropertyName("recordsScanned")]
    public int RecordsScanned { get; set; }

    [JsonPropertyName("validRecords")]
    public int ValidRecords { get; set; }

    [JsonPropertyName("validRecordsPct")]
    public double ValidRecordsPct { get; set; }

    [JsonPropertyName("needsReview")]
    public int NeedsReview { get; set; }

    [JsonPropertyName("needsReviewPct")]
    public double NeedsReviewPct { get; set; }

    [JsonPropertyName("criticalErrors")]
    public int CriticalErrors { get; set; }

    [JsonPropertyName("criticalErrorsPct")]
    public double CriticalErrorsPct { get; set; }
}

public class PreviewPagination
{
    [JsonPropertyName("currentPage")]
    public int CurrentPage { get; set; } = 1;

    [JsonPropertyName("pageSize")]
    public int PageSize { get; set; } = 10;

    [JsonPropertyName("totalRecords")]
    public int TotalRecords { get; set; }

    [JsonPropertyName("totalPages")]
    public int TotalPages { get; set; }

    [JsonPropertyName("filteredRecords")]
    public int FilteredRecords { get; set; }
}

public class PreviewIssue
{
    [JsonPropertyName("field")]
    public string? Field { get; set; }

    [JsonPropertyName("severity")]
    public string Severity { get; set; } = "Warning"; // "Warning" | "Error"

    [JsonPropertyName("code")]
    public string Code { get; set; } = string.Empty;

    [JsonPropertyName("message")]
    public string Message { get; set; } = string.Empty;
}

public class PreviewRecord
{
    [JsonPropertyName("id")]
    public string Id { get; set; } = string.Empty;

    [JsonPropertyName("tenantId")]
    public string TenantId { get; set; } = string.Empty;

    [JsonPropertyName("provenanceId")]
    public string? ProvenanceId { get; set; }

    [JsonPropertyName("poleId")]
    public string PoleId { get; set; } = string.Empty;

    [JsonPropertyName("sourceRecordId")]
    public string SourceRecordId { get; set; } = string.Empty;

    [JsonPropertyName("source")]
    public string Source { get; set; } = "Excel"; // "Excel" | "GIS" | "Third Party"

    [JsonPropertyName("latitude")]
    public double? Latitude { get; set; }

    [JsonPropertyName("longitude")]
    public double? Longitude { get; set; }

    [JsonPropertyName("address")]
    public string? Address { get; set; }

    [JsonPropertyName("material")]
    public string? Material { get; set; }

    [JsonPropertyName("class")]
    public string? Class { get; set; }

    [JsonPropertyName("heightFt")]
    public double? HeightFt { get; set; }

    [JsonPropertyName("installYear")]
    public int? InstallYear { get; set; }

    [JsonPropertyName("owner")]
    public string? Owner { get; set; }

    [JsonPropertyName("ingestionStatus")]
    public string IngestionStatus { get; set; } = "Validated";

    [JsonPropertyName("dataQualityScore")]
    public int DataQualityScore { get; set; } = 100;

    [JsonPropertyName("validationStatus")]
    public string ValidationStatus { get; set; } = "Valid"; // "Valid" | "Warning" | "Error"

    [JsonPropertyName("lastSourceUpdate")]
    public string? LastSourceUpdate { get; set; }

    [JsonPropertyName("issues")]
    public List<PreviewIssue> Issues { get; set; } = new();

    [JsonPropertyName("rawFields")]
    public Dictionary<string, string> RawFields { get; set; } = new();
}

public class DataPreviewResponse
{
    [JsonPropertyName("fileInfo")]
    public PreviewFileInfo FileInfo { get; set; } = new();

    [JsonPropertyName("summary")]
    public PreviewSummary Summary { get; set; } = new();

    [JsonPropertyName("pagination")]
    public PreviewPagination Pagination { get; set; } = new();

    [JsonPropertyName("records")]
    public List<PreviewRecord> Records { get; set; } = new();
}
