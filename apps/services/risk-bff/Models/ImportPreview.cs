using System.Text.Json.Serialization;

namespace RiskBff.Models;

public sealed record ImportPreviewResponse(
    [property: JsonPropertyName("import_id")] string ImportId,
    [property: JsonPropertyName("tenant_id")] string TenantId,
    [property: JsonPropertyName("file_name")] string FileName,
    [property: JsonPropertyName("uploaded_on")] DateTime UploadedOn,
    [property: JsonPropertyName("uploaded_by")] string? UploadedBy,
    [property: JsonPropertyName("data_preview")] ImportDataPreview DataPreview);

public sealed record ImportDataPreview(
    [property: JsonPropertyName("columns")] IReadOnlyList<string> Columns,
    [property: JsonPropertyName("rows")] IReadOnlyList<ImportPreviewRow> Rows,
    [property: JsonPropertyName("page")] int Page,
    [property: JsonPropertyName("page_size")] int PageSize,
    [property: JsonPropertyName("total_records")] int TotalRecords,
    [property: JsonPropertyName("total_matching_records")] int TotalMatchingRecords);

public sealed record ImportPreviewRow(
    [property: JsonPropertyName("row_number")] int RowNumber,
    [property: JsonPropertyName("values")] IReadOnlyList<string?> Values);