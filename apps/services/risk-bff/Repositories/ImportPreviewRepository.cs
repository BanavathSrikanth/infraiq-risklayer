using Dapper;
using Npgsql;

namespace RiskBff.Repositories;

public sealed record ImportFileRecord(
    string ImportId,
    string TenantId,
    string FileName,
    string StoredFileName,
    DateTime UploadedOn,
    string? UploadedBy);

public sealed class ImportPreviewRepository(IServiceProvider serviceProvider)
{
    private const string SelectImportSql = """
        SELECT document_id AS "ImportId",
               tenant_id AS "TenantId",
               file_name AS "FileName",
               stored_file_name AS "StoredFileName",
               uploaded_at AS "UploadedOn",
               uploaded_by AS "UploadedBy"
        FROM evidence_uploads
        WHERE document_id = @ImportId
          AND tenant_id = @TenantId
        """;

    public bool IsConfigured => serviceProvider.GetService<NpgsqlDataSource>() is not null;

    public async Task<ImportFileRecord?> GetForTenantAsync(
        string importId,
        string tenantId,
        CancellationToken cancellationToken)
    {
        var dataSource = serviceProvider.GetService<NpgsqlDataSource>();
        if (dataSource is null)
        {
            return null;
        }

        await using var connection = await dataSource.OpenConnectionAsync(cancellationToken);
        return await connection.QuerySingleOrDefaultAsync<ImportFileRecord>(new CommandDefinition(
            SelectImportSql,
            new { ImportId = importId, TenantId = tenantId },
            cancellationToken: cancellationToken));
    }
}