using Microsoft.VisualBasic.FileIO;
using RiskBff.Models;

namespace RiskBff.Services;

public sealed record CsvImportPreviewPage(
    IReadOnlyList<string> Columns,
    IReadOnlyList<ImportPreviewRow> Rows,
    int TotalRecords,
    int TotalMatchingRecords);

public sealed class CsvImportPreviewReader
{
    public CsvImportPreviewPage ReadPage(
        string path,
        int page,
        int pageSize,
        string? search,
        string? ingestionStatus,
        CancellationToken cancellationToken)
    {
        using var parser = new TextFieldParser(path)
        {
            HasFieldsEnclosedInQuotes = true,
            TrimWhiteSpace = true,
        };
        parser.SetDelimiters(",");

        var headerFields = parser.EndOfData ? [] : parser.ReadFields() ?? [];
        if (headerFields.Length == 0)
        {
            throw new InvalidDataException("The CSV file must contain a header row.");
        }

        var columns = headerFields
            .Select((header, index) => string.IsNullOrWhiteSpace(header) ? $"Column {index + 1}" : header)
            .ToList();
        var rows = new List<ImportPreviewRow>(pageSize);
        var totalRecords = 0;
        var totalMatchingRecords = 0;
        var firstRecordIndex = (long)(page - 1) * pageSize;
        var searchText = search?.Trim();
        var ingestionStatusText = ingestionStatus?.Trim();
        var ingestionStatusIndex = string.IsNullOrEmpty(ingestionStatusText)
            ? -1
            : columns.FindIndex(column => NormalizeHeader(column) == "ingestionstatus");
        if (!string.IsNullOrEmpty(ingestionStatusText) && ingestionStatusIndex < 0)
        {
            throw new InvalidDataException("The CSV does not contain an Ingestion Status column.");
        }

        while (!parser.EndOfData)
        {
            cancellationToken.ThrowIfCancellationRequested();
            var fields = parser.ReadFields();
            if (fields is null || fields.All(string.IsNullOrWhiteSpace))
            {
                continue;
            }

            totalRecords++;
            if (fields.Length > columns.Count)
            {
                for (var index = columns.Count; index < fields.Length; index++)
                {
                    columns.Add($"Column {index + 1}");
                }
            }

            if (!string.IsNullOrEmpty(searchText) && !fields.Any(value =>
                    value?.Contains(searchText, StringComparison.OrdinalIgnoreCase) == true))
            {
                continue;
            }

            if (!string.IsNullOrEmpty(ingestionStatusText) &&
                (fields.Length <= ingestionStatusIndex ||
                 !string.Equals(fields[ingestionStatusIndex]?.Trim(), ingestionStatusText, StringComparison.OrdinalIgnoreCase)))
            {
                continue;
            }

            if (totalMatchingRecords >= firstRecordIndex && rows.Count < pageSize)
            {
                rows.Add(new ImportPreviewRow(totalRecords, fields));
            }

            totalMatchingRecords++;
        }

        var paddedRows = rows
            .Select(row => row with
            {
                Values = row.Values.Concat(Enumerable.Repeat<string?>(null, columns.Count - row.Values.Count)).ToArray(),
            })
            .ToArray();

        return new CsvImportPreviewPage(columns, paddedRows, totalRecords, totalMatchingRecords);
    }

    private static string NormalizeHeader(string header) =>
        new(header.Where(char.IsLetterOrDigit).Select(char.ToLowerInvariant).ToArray());
}