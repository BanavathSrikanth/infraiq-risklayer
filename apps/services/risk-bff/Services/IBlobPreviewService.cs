using RiskBff.Models;

namespace RiskBff.Services;

public interface IBlobPreviewService
{
    Task<DataPreviewResponse> GetPreviewAsync(DataPreviewQueryParams queryParams, CancellationToken cancellationToken = default);
}
