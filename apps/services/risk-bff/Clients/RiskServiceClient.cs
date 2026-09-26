using System.Net.Http.Json;
using System.Text.Json;
using RiskBff.Models;

namespace RiskBff.Clients;

public interface IRiskServiceClient
{
    Task<RiskIngestResponse?> IngestBlobAsync(RiskIngestRequest request, CancellationToken cancellationToken = default);
    Task<JsonElement?> CalculateRiskAsync(JsonElement request, CancellationToken cancellationToken = default);
    Task<HttpResponseMessage> GetLatestRiskAsync(string assetId, string tenantId, CancellationToken cancellationToken = default);
    Task<HttpResponseMessage> CalculatePolePriorityAsync(PolePriorityRequest request, CancellationToken cancellationToken = default);
    Task<HttpResponseMessage> GetRiskHistoryAsync(string assetId, string tenantId, CancellationToken cancellationToken = default);
}

public class RiskServiceClient(HttpClient httpClient) : IRiskServiceClient
{
    public async Task<RiskIngestResponse?> IngestBlobAsync(RiskIngestRequest request, CancellationToken cancellationToken = default)
    {
        var response = await httpClient.PostAsJsonAsync("/api/v1/risks/ingest/blob", request, cancellationToken);
        response.EnsureSuccessStatusCode();

        return await response.Content.ReadFromJsonAsync<RiskIngestResponse>(cancellationToken: cancellationToken);
    }

    public async Task<JsonElement?> CalculateRiskAsync(JsonElement request, CancellationToken cancellationToken = default)
    {
        var response = await httpClient.PostAsJsonAsync("/api/v1/risks/calculate", request, cancellationToken);
        response.EnsureSuccessStatusCode();

        return await response.Content.ReadFromJsonAsync<JsonElement>(cancellationToken: cancellationToken);
    }

    public Task<HttpResponseMessage> GetLatestRiskAsync(string assetId, string tenantId, CancellationToken cancellationToken = default)
    {
        var path = $"/api/v1/risks/latest/{Uri.EscapeDataString(assetId)}?tenant_id={Uri.EscapeDataString(tenantId)}";
        return httpClient.GetAsync(path, cancellationToken);
    }

    public Task<HttpResponseMessage> CalculatePolePriorityAsync(PolePriorityRequest request, CancellationToken cancellationToken = default)
    {
        return httpClient.PostAsJsonAsync("/api/v1/risks/pole-priority", request, cancellationToken);
    }

    public Task<HttpResponseMessage> GetRiskHistoryAsync(string assetId, string tenantId, CancellationToken cancellationToken = default)
    {
        var path = $"/api/v1/risks/history/{Uri.EscapeDataString(assetId)}?tenant_id={Uri.EscapeDataString(tenantId)}";
        return httpClient.GetAsync(path, cancellationToken);
    }
}
