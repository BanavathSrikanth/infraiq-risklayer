namespace RiskBff.Models;

public class RiskIngestRequest
{
    public string BlobName { get; set; } = string.Empty;
    public string? TenantId { get; set; }
}

public class RiskIngestResponse
{
    public List<object> Results { get; set; } = new();
    public List<object> Errors { get; set; } = new();
}
