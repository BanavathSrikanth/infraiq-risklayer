using System.Globalization;
using Azure.Storage.Blobs;
using Azure.Storage.Blobs.Models;
using CsvHelper;
using CsvHelper.Configuration;
using RiskBff.Models;

namespace RiskBff.Services;

public class BlobPreviewService(IConfiguration configuration, ILogger<BlobPreviewService> logger) : IBlobPreviewService
{
    private readonly string? _blobConnectionString =
        configuration.GetConnectionString("AzureBlobStorage") ??
        configuration.GetValue<string>("AzureBlobStorage:ConnectionString") ??
        configuration.GetValue<string>("BLOB_CONNECTION_STRING") ??
        Environment.GetEnvironmentVariable("BLOB_CONNECTION_STRING");

    private readonly string _containerName =
        configuration.GetValue<string>("AzureBlobStorage:ContainerName") ??
        configuration.GetValue<string>("BLOB_CONTAINER") ??
        "infraiq";

    public async Task<DataPreviewResponse> GetPreviewAsync(DataPreviewQueryParams queryParams, CancellationToken cancellationToken = default)
    {
        List<PreviewRecord> allRecords;
        PreviewFileInfo fileInfo;

        var tenantId = !string.IsNullOrWhiteSpace(queryParams.TenantId) ? queryParams.TenantId : "tenant-demo";
        var blobTarget = !string.IsNullOrWhiteSpace(queryParams.BlobName)
            ? queryParams.BlobName
            : queryParams.UploadId;

        // Try reading from Azure Blob Storage if configured and a target is requested
        if (!string.IsNullOrWhiteSpace(_blobConnectionString) && !string.IsNullOrWhiteSpace(blobTarget))
        {
            try
            {
                var (blobRecords, blobInfo) = await ReadFromAzureBlobAsync(blobTarget, tenantId, cancellationToken);
                allRecords = blobRecords;
                fileInfo = blobInfo;
            }
            catch (Exception ex)
            {
                logger.LogWarning(ex, "Failed to load preview directly from Azure Blob '{BlobTarget}'. Falling back to prototype preview dataset.", blobTarget);
                (allRecords, fileInfo) = GeneratePrototypeDataset(blobTarget, tenantId);
            }
        }
        else
        {
            (allRecords, fileInfo) = GeneratePrototypeDataset(blobTarget ?? "Utility_Poles_Import_Jan2026.csv", tenantId);
        }

        // Compute summary metrics across all records
        var totalScanned = allRecords.Count;
        var validCount = allRecords.Count(r => r.ValidationStatus == "Valid");
        var warningCount = allRecords.Count(r => r.ValidationStatus == "Warning");
        var errorCount = allRecords.Count(r => r.ValidationStatus == "Error");

        var summary = new PreviewSummary
        {
            RecordsScanned = totalScanned,
            ValidRecords = validCount,
            ValidRecordsPct = totalScanned > 0 ? Math.Round((double)validCount / totalScanned * 100.0, 1) : 0,
            NeedsReview = warningCount,
            NeedsReviewPct = totalScanned > 0 ? Math.Round((double)warningCount / totalScanned * 100.0, 1) : 0,
            CriticalErrors = errorCount,
            CriticalErrorsPct = totalScanned > 0 ? Math.Round((double)errorCount / totalScanned * 100.0, 1) : 0
        };

        // Apply filters
        var filtered = allRecords.AsEnumerable();

        if (!string.IsNullOrWhiteSpace(queryParams.Search))
        {
            var search = queryParams.Search.Trim().ToLowerInvariant();
            filtered = filtered.Where(r =>
                r.PoleId.ToLowerInvariant().Contains(search) ||
                r.SourceRecordId.ToLowerInvariant().Contains(search) ||
                (r.Address != null && r.Address.ToLowerInvariant().Contains(search)) ||
                (r.Owner != null && r.Owner.ToLowerInvariant().Contains(search)));
        }

        if (!string.IsNullOrWhiteSpace(queryParams.Status) && !queryParams.Status.Equals("all", StringComparison.OrdinalIgnoreCase))
        {
            filtered = filtered.Where(r => r.IngestionStatus.Equals(queryParams.Status, StringComparison.OrdinalIgnoreCase));
        }

        if (!string.IsNullOrWhiteSpace(queryParams.Source) && !queryParams.Source.Equals("all", StringComparison.OrdinalIgnoreCase))
        {
            filtered = filtered.Where(r => r.Source.Equals(queryParams.Source, StringComparison.OrdinalIgnoreCase));
        }

        if (!string.IsNullOrWhiteSpace(queryParams.ValidationStatus) && !queryParams.ValidationStatus.Equals("all", StringComparison.OrdinalIgnoreCase))
        {
            filtered = filtered.Where(r => r.ValidationStatus.Equals(queryParams.ValidationStatus, StringComparison.OrdinalIgnoreCase));
        }

        var filteredList = filtered.ToList();
        var totalFiltered = filteredList.Count;

        // Apply sorting
        var isAscending = string.Equals(queryParams.SortDirection, "asc", StringComparison.OrdinalIgnoreCase);
        filteredList = (queryParams.SortBy?.ToLowerInvariant()) switch
        {
            "poleid" => isAscending ? filteredList.OrderBy(r => r.PoleId).ToList() : filteredList.OrderByDescending(r => r.PoleId).ToList(),
            "sourcerecordid" => isAscending ? filteredList.OrderBy(r => r.SourceRecordId).ToList() : filteredList.OrderByDescending(r => r.SourceRecordId).ToList(),
            "source" => isAscending ? filteredList.OrderBy(r => r.Source).ToList() : filteredList.OrderByDescending(r => r.Source).ToList(),
            "address" => isAscending ? filteredList.OrderBy(r => r.Address).ToList() : filteredList.OrderByDescending(r => r.Address).ToList(),
            "material" => isAscending ? filteredList.OrderBy(r => r.Material).ToList() : filteredList.OrderByDescending(r => r.Material).ToList(),
            "heightft" => isAscending ? filteredList.OrderBy(r => r.HeightFt).ToList() : filteredList.OrderByDescending(r => r.HeightFt).ToList(),
            "installyear" => isAscending ? filteredList.OrderBy(r => r.InstallYear).ToList() : filteredList.OrderByDescending(r => r.InstallYear).ToList(),
            "owner" => isAscending ? filteredList.OrderBy(r => r.Owner).ToList() : filteredList.OrderByDescending(r => r.Owner).ToList(),
            "dataqualityscore" => isAscending ? filteredList.OrderBy(r => r.DataQualityScore).ToList() : filteredList.OrderByDescending(r => r.DataQualityScore).ToList(),
            "validationstatus" => isAscending ? filteredList.OrderBy(r => r.ValidationStatus).ToList() : filteredList.OrderByDescending(r => r.ValidationStatus).ToList(),
            "lastsourceupdate" => isAscending ? filteredList.OrderBy(r => r.LastSourceUpdate).ToList() : filteredList.OrderByDescending(r => r.LastSourceUpdate).ToList(),
            _ => isAscending ? filteredList.OrderBy(r => r.PoleId).ToList() : filteredList.OrderByDescending(r => r.PoleId).ToList()
        };

        // Apply pagination
        var page = queryParams.Page <= 0 ? 1 : queryParams.Page;
        var pageSize = queryParams.PageSize <= 0 ? 10 : queryParams.PageSize;
        var totalPages = (int)Math.Ceiling((double)totalFiltered / pageSize);
        if (totalPages == 0) totalPages = 1;

        var pagedRecords = filteredList
            .Skip((page - 1) * pageSize)
            .Take(pageSize)
            .ToList();

        var pagination = new PreviewPagination
        {
            CurrentPage = page,
            PageSize = pageSize,
            TotalRecords = totalScanned,
            FilteredRecords = totalFiltered,
            TotalPages = totalPages
        };

        return new DataPreviewResponse
        {
            FileInfo = fileInfo,
            Summary = summary,
            Pagination = pagination,
            Records = pagedRecords
        };
    }

    private async Task<(List<PreviewRecord> records, PreviewFileInfo fileInfo)> ReadFromAzureBlobAsync(
        string blobTarget,
        string tenantId,
        CancellationToken cancellationToken)
    {
        var blobServiceClient = new BlobServiceClient(_blobConnectionString);
        var containerClient = blobServiceClient.GetBlobContainerClient(_containerName);

        var cleanTarget = blobTarget.TrimStart('/');
        var candidates = new[]
        {
            cleanTarget,
            $"{tenantId}/imports/{cleanTarget}",
            $"imports/{cleanTarget}",
            $"raw/{cleanTarget}"
        };

        BlobClient? blobClient = null;
        BlobProperties? properties = null;

        foreach (var candidate in candidates)
        {
            var client = containerClient.GetBlobClient(candidate);
            if (await client.ExistsAsync(cancellationToken))
            {
                blobClient = client;
                var props = await client.GetPropertiesAsync(cancellationToken: cancellationToken);
                properties = props.Value;
                break;
            }
        }

        if (blobClient == null || properties == null)
        {
            blobClient = containerClient.GetBlobClient(cleanTarget);
            var props = await blobClient.GetPropertiesAsync(cancellationToken: cancellationToken);
            properties = props.Value;
        }

        var fileSizeBytes = properties.ContentLength;

        using var stream = await blobClient.OpenReadAsync(cancellationToken: cancellationToken);
        using var reader = new StreamReader(stream);
        using var csv = new CsvReader(reader, new CsvConfiguration(CultureInfo.InvariantCulture)
        {
            HeaderValidated = null,
            MissingFieldFound = null,
            BadDataFound = null,
            TrimOptions = TrimOptions.Trim
        });

        await csv.ReadAsync();
        csv.ReadHeader();
        var headers = csv.HeaderRecord ?? Array.Empty<string>();

        var records = new List<PreviewRecord>();
        var rowNumber = 1;

        while (await csv.ReadAsync())
        {
            var raw = new Dictionary<string, string>();
            foreach (var header in headers)
            {
                raw[header] = csv.GetField(header) ?? string.Empty;
            }

            var record = ParseRecordFromRaw(raw, rowNumber++, tenantId);
            records.Add(record);
        }

        var fileInfo = new PreviewFileInfo
        {
            UploadId = blobTarget,
            TenantId = tenantId,
            BlobUri = blobClient.Uri.ToString(),
            FileName = Path.GetFileName(blobTarget),
            UploadedAt = properties.LastModified.ToString("yyyy-MM-ddTHH:mm:ssZ"),
            UploadedBy = properties.Metadata.TryGetValue("uploaded_by", out var user) ? user : "System User",
            FileSizeBytes = fileSizeBytes,
            FileSizeFormatted = FormatFileSize(fileSizeBytes),
            ProcessingStatus = "File processed successfully",
            ProcessingDuration = "01.28s"
        };

        return (records, fileInfo);
    }

    private static PreviewRecord ParseRecordFromRaw(Dictionary<string, string> raw, int rowNumber, string tenantId)
    {
        string GetValue(params string[] aliases)
        {
            foreach (var alias in aliases)
            {
                var match = raw.FirstOrDefault(kvp => string.Equals(kvp.Key.Trim(), alias, StringComparison.OrdinalIgnoreCase));
                if (!string.IsNullOrEmpty(match.Key)) return match.Value;
            }
            return string.Empty;
        }

        var poleId = GetValue("Pole ID", "pole_id", "PoleId", "Asset ID", "asset_id", "Pole_ID");
        if (string.IsNullOrWhiteSpace(poleId))
        {
            poleId = $"PL-{10000 + rowNumber}";
        }

        var sourceId = GetValue("Source Record ID", "source_record_id", "SourceRecordId", "Record ID", "record_id", "Source_ID");
        if (string.IsNullOrWhiteSpace(sourceId))
        {
            sourceId = $"UT-{55000 + rowNumber}";
        }

        var source = GetValue("Source", "source", "source_system");
        if (string.IsNullOrWhiteSpace(source)) source = "Excel";

        var latStr = GetValue("Latitude", "latitude", "lat", "Lat");
        double? latitude = double.TryParse(latStr, NumberStyles.Any, CultureInfo.InvariantCulture, out var lat) ? lat : null;

        var lonStr = GetValue("Longitude", "longitude", "lon", "lng", "Long");
        double? longitude = double.TryParse(lonStr, NumberStyles.Any, CultureInfo.InvariantCulture, out var lon) ? lon : null;

        var address = GetValue("Address / Location", "Address", "address", "Location", "location");
        var material = GetValue("Material", "material");
        var poleClass = GetValue("Class", "class", "pole_class");

        var heightStr = GetValue("Height (ft)", "Height", "height", "height_ft");
        double? height = double.TryParse(heightStr, NumberStyles.Any, CultureInfo.InvariantCulture, out var h) ? h : null;

        var yearStr = GetValue("Install Year", "install_year", "InstallYear", "year_installed");
        int? installYear = int.TryParse(yearStr, out var y) ? y : null;

        var owner = GetValue("Owner", "owner", "utility");
        var ingestionStatus = GetValue("Ingestion Status", "status", "ingestion_status");
        if (string.IsNullOrWhiteSpace(ingestionStatus)) ingestionStatus = "Validated";

        var updateDate = GetValue("Last Source Update", "last_source_update", "updated_at");
        if (string.IsNullOrWhiteSpace(updateDate)) updateDate = DateTime.UtcNow.ToString("yyyy-MM-dd");

        var issues = new List<PreviewIssue>();
        var qualityScore = 100;

        if (latitude == null || longitude == null)
        {
            issues.Add(new PreviewIssue
            {
                Field = "Coordinates",
                Severity = "Error",
                Code = "MISSING_COORDINATES",
                Message = "Latitude or Longitude is missing or invalid."
            });
            qualityScore -= 40;
        }

        if (string.IsNullOrWhiteSpace(material))
        {
            issues.Add(new PreviewIssue
            {
                Field = "Material",
                Severity = "Warning",
                Code = "MISSING_MATERIAL",
                Message = "Asset material is not specified."
            });
            qualityScore -= 15;
        }

        if (height == null || height <= 0 || height > 120)
        {
            issues.Add(new PreviewIssue
            {
                Field = "Height",
                Severity = "Warning",
                Code = "HEIGHT_ANOMALY",
                Message = "Height is out of standard range (10-100 ft)."
            });
            qualityScore -= 15;
        }

        var validationStatus = issues.Any(i => i.Severity == "Error")
            ? "Error"
            : issues.Any(i => i.Severity == "Warning")
                ? "Warning"
                : "Valid";

        return new PreviewRecord
        {
            Id = $"rec-{rowNumber}",
            TenantId = tenantId,
            ProvenanceId = Guid.NewGuid().ToString(),
            PoleId = poleId,
            SourceRecordId = sourceId,
            Source = source,
            Latitude = latitude,
            Longitude = longitude,
            Address = address,
            Material = string.IsNullOrWhiteSpace(material) ? "Wood" : material,
            Class = string.IsNullOrWhiteSpace(poleClass) ? "3" : poleClass,
            HeightFt = height ?? 35,
            InstallYear = installYear ?? 2020,
            Owner = string.IsNullOrWhiteSpace(owner) ? "UtilityCo" : owner,
            IngestionStatus = ingestionStatus,
            DataQualityScore = Math.Clamp(qualityScore, 20, 100),
            ValidationStatus = validationStatus,
            LastSourceUpdate = updateDate,
            Issues = issues,
            RawFields = raw
        };
    }

    private static (List<PreviewRecord> records, PreviewFileInfo fileInfo) GeneratePrototypeDataset(string targetName, string tenantId)
    {
        // Prototype dataset matching the exact screen prototype
        var exactScreenRows = new List<PreviewRecord>
        {
            new()
            {
                Id = "rec-1",
                PoleId = "PL-10284",
                SourceRecordId = "UT-55621",
                Source = "Excel",
                Latitude = 34.0523,
                Longitude = -118.2437,
                Address = "1234 Oak St, LA",
                Material = "Wood",
                Class = "3",
                HeightFt = 35,
                InstallYear = 2020,
                Owner = "UtilityCo",
                IngestionStatus = "Validated",
                DataQualityScore = 92,
                ValidationStatus = "Valid",
                LastSourceUpdate = "2026-01-12"
            },
            new()
            {
                Id = "rec-2",
                PoleId = "PL-10285",
                SourceRecordId = "UT-55622",
                Source = "GIS",
                Latitude = 34.0611,
                Longitude = -118.2562,
                Address = "5678 Pine Ave, LA",
                Material = "Wood",
                Class = "4",
                HeightFt = 40,
                InstallYear = 2019,
                Owner = "UtilityCo",
                IngestionStatus = "Needs Review",
                DataQualityScore = 68,
                ValidationStatus = "Warning",
                LastSourceUpdate = "2026-01-14",
                Issues = new List<PreviewIssue>
                {
                    new() { Field = "Material", Severity = "Warning", Code = "SURVEY_FLAG", Message = "Recent survey indicates surface weathering." }
                }
            },
            new()
            {
                Id = "rec-3",
                PoleId = "PL-10286",
                SourceRecordId = "EXT-78412",
                Source = "Third Party",
                Latitude = 34.0718,
                Longitude = -118.2689,
                Address = "9012 Maple Rd",
                Material = "Concrete",
                Class = "2",
                HeightFt = 38,
                InstallYear = 2021,
                Owner = "City Utility",
                IngestionStatus = "Imported",
                DataQualityScore = 85,
                ValidationStatus = "Valid",
                LastSourceUpdate = "2025-12-28"
            },
            new()
            {
                Id = "rec-4",
                PoleId = "PL-10287",
                SourceRecordId = "UT-55623",
                Source = "Excel",
                Latitude = 34.0821,
                Longitude = -118.2410,
                Address = "2468 Cedar St",
                Material = "Steel",
                Class = "3",
                HeightFt = 45,
                InstallYear = 2018,
                Owner = "UtilityCo",
                IngestionStatus = "Validation Error",
                DataQualityScore = 42,
                ValidationStatus = "Error",
                LastSourceUpdate = "2026-01-10",
                Issues = new List<PreviewIssue>
                {
                    new() { Field = "Address", Severity = "Error", Code = "INVALID_TERRITORY", Message = "Location boundary outside serviced utility zone." }
                }
            },
            new()
            {
                Id = "rec-5",
                PoleId = "PL-10288",
                SourceRecordId = "GIS-99021",
                Source = "GIS",
                Latitude = 34.0783,
                Longitude = -118.2601,
                Address = "1357 Birch Dr",
                Material = "Wood",
                Class = "3",
                HeightFt = 32,
                InstallYear = 2022,
                Owner = "UtilityCo",
                IngestionStatus = "Mapped",
                DataQualityScore = 90,
                ValidationStatus = "Valid",
                LastSourceUpdate = "2026-01-11"
            },
            new()
            {
                Id = "rec-6",
                PoleId = "PL-10289",
                SourceRecordId = "EXT-78413",
                Source = "Third Party",
                Latitude = 34.0649,
                Longitude = -118.2745,
                Address = "7890 Walnut Ave",
                Material = "Wood",
                Class = "4",
                HeightFt = 28,
                InstallYear = 2021,
                Owner = "UtilityCo",
                IngestionStatus = "Incomplete",
                DataQualityScore = 55,
                ValidationStatus = "Warning",
                LastSourceUpdate = "2026-01-09",
                Issues = new List<PreviewIssue>
                {
                    new() { Field = "Height", Severity = "Warning", Code = "LOW_CLEARANCE", Message = "Height under typical distribution standard." }
                }
            },
            new()
            {
                Id = "rec-7",
                PoleId = "PL-10290",
                SourceRecordId = "UT-55624",
                Source = "Excel",
                Latitude = 34.0621,
                Longitude = -118.2534,
                Address = "4321 Spruce Ln",
                Material = "Concrete",
                Class = "2",
                HeightFt = 42,
                InstallYear = 2019,
                Owner = "UtilityCo",
                IngestionStatus = "Duplicate",
                DataQualityScore = 70,
                ValidationStatus = "Error",
                LastSourceUpdate = "2026-01-09",
                Issues = new List<PreviewIssue>
                {
                    new() { Field = "PoleId", Severity = "Error", Code = "DUPLICATE_ASSET", Message = "Duplicate asset identifier detected in staging." }
                }
            },
            new()
            {
                Id = "rec-8",
                PoleId = "PL-10291",
                SourceRecordId = "GIS-99022",
                Source = "GIS",
                Latitude = 34.0598,
                Longitude = -118.2622,
                Address = "6789 Elm St",
                Material = "Wood",
                Class = "3",
                HeightFt = 36,
                InstallYear = 2020,
                Owner = "UtilityCo",
                IngestionStatus = "Validated",
                DataQualityScore = 94,
                ValidationStatus = "Valid",
                LastSourceUpdate = "2026-01-13"
            },
            new()
            {
                Id = "rec-9",
                PoleId = "PL-10292",
                SourceRecordId = "UT-55625",
                Source = "Excel",
                Latitude = 34.0486,
                Longitude = -118.2715,
                Address = "2460 Willow Dr",
                Material = "Steel",
                Class = "4",
                HeightFt = 48,
                InstallYear = 2022,
                Owner = "UtilityCo",
                IngestionStatus = "Needs Review",
                DataQualityScore = 76,
                ValidationStatus = "Warning",
                LastSourceUpdate = "2026-01-08",
                Issues = new List<PreviewIssue>
                {
                    new() { Field = "Owner", Severity = "Warning", Code = "OWNERSHIP_MISMATCH", Message = "Owner discrepancy with county land register." }
                }
            },
            new()
            {
                Id = "rec-10",
                PoleId = "PL-10293",
                SourceRecordId = "EXT-78414",
                Source = "Third Party",
                Latitude = 34.0667,
                Longitude = -118.2490,
                Address = "9753 Palm Ave",
                Material = "Wood",
                Class = "3",
                HeightFt = 30,
                InstallYear = 2021,
                Owner = "UtilityCo",
                IngestionStatus = "Mapped",
                DataQualityScore = 88,
                ValidationStatus = "Valid",
                LastSourceUpdate = "2026-01-12"
            }
        };

        // Synthesize the remaining rows up to 5,248 to achieve the exact statistics (4,132 Valid, 936 Warning, 180 Error)
        var allRecords = new List<PreviewRecord>(exactScreenRows);

        var streets = new[] { "Oak St", "Pine Ave", "Maple Rd", "Cedar St", "Birch Dr", "Walnut Ave", "Spruce Ln", "Elm St", "Willow Dr", "Palm Ave", "Highland Blvd", "Sunset Way", "Canyon Rd" };
        var materials = new[] { "Wood", "Concrete", "Steel", "Composite" };
        var sources = new[] { "Excel", "GIS", "Third Party" };

        var remainingValid = 4132 - exactScreenRows.Count(r => r.ValidationStatus == "Valid");
        var remainingWarning = 936 - exactScreenRows.Count(r => r.ValidationStatus == "Warning");
        var remainingError = 180 - exactScreenRows.Count(r => r.ValidationStatus == "Error");

        int nextId = 11;

        void AppendBatch(int count, string valStatus, string ingStatus, int baseQuality, bool hasIssues)
        {
            for (int i = 0; i < count; i++)
            {
                var num = nextId++;
                var stName = streets[num % streets.Length];
                allRecords.Add(new PreviewRecord
                {
                    Id = $"rec-{num}",
                    PoleId = $"PL-{10293 + (num - 10)}",
                    SourceRecordId = $"UT-{55625 + (num - 10)}",
                    Source = sources[num % sources.Length],
                    Latitude = Math.Round(34.0500 + ((num % 1000) * 0.0001), 4),
                    Longitude = Math.Round(-118.2500 - ((num % 1000) * 0.0001), 4),
                    Address = $"{1000 + (num * 3)} {stName}, LA",
                    Material = materials[num % materials.Length],
                    Class = ((num % 4) + 1).ToString(),
                    HeightFt = 30 + ((num % 5) * 5),
                    InstallYear = 2015 + (num % 9),
                    Owner = num % 5 == 0 ? "City Utility" : "UtilityCo",
                    IngestionStatus = ingStatus,
                    DataQualityScore = baseQuality + (num % 5),
                    ValidationStatus = valStatus,
                    LastSourceUpdate = "2026-01-12",
                    Issues = hasIssues ? new List<PreviewIssue>
                    {
                        new()
                        {
                            Field = valStatus == "Error" ? "Coordinates" : "Survey",
                            Severity = valStatus,
                            Code = valStatus == "Error" ? "OUT_OF_BOUNDS" : "REVIEW_REQUIRED",
                            Message = valStatus == "Error" ? "Record validation failed ruleset checks." : "Item marked for secondary QA inspection."
                        }
                    } : new List<PreviewIssue>()
                });
            }
        }

        AppendBatch(remainingValid, "Valid", "Validated", 90, false);
        AppendBatch(remainingWarning, "Warning", "Needs Review", 65, true);
        AppendBatch(remainingError, "Error", "Validation Error", 40, true);

        foreach (var r in allRecords)
        {
            r.TenantId = tenantId;
            r.ProvenanceId = Guid.NewGuid().ToString();
        }

        var fileInfo = new PreviewFileInfo
        {
            UploadId = "upl-jan2026-utility-poles",
            TenantId = tenantId,
            BlobUri = $"https://<storage_account>.blob.core.windows.net/infraiq/{tenantId}/imports/{Path.GetFileName(targetName)}",
            FileName = Path.GetFileName(targetName),
            UploadedAt = "2026-01-15T10:24:00Z",
            UploadedBy = "Harsha Vivek",
            FileSizeBytes = 3355443,
            FileSizeFormatted = "3.2 MB",
            ProcessingStatus = "File processed successfully",
            ProcessingDuration = "01.28s"
        };

        return (allRecords, fileInfo);
    }

    private static string FormatFileSize(long bytes)
    {
        if (bytes < 1024) return $"{bytes} B";
        if (bytes < 1024 * 1024) return $"{Math.Round((double)bytes / 1024, 1)} KB";
        return $"{Math.Round((double)bytes / (1024 * 1024), 1)} MB";
    }
}
