using System.Net.Http.Json;
using System.Text.Json;
using RiskBff.Models;

namespace RiskBff.Clients;

public interface IRiskServiceClient
{
    Task<RiskIngestResponse?> IngestBlobAsync(RiskIngestRequest request, CancellationToken cancellationToken = default);
    Task<JsonElement?> CalculateRiskAsync(JsonElement request, CancellationToken cancellationToken = default);
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
}
