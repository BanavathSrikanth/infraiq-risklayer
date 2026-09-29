CREATE TABLE IF NOT EXISTS evidence_uploads (
    document_id text PRIMARY KEY,
    asset_id text NOT NULL,
    tenant_id text NOT NULL,
    file_name text NOT NULL,
    stored_file_name text NOT NULL,
    record_count bigint NOT NULL DEFAULT 0,
    uploaded_at timestamptz NOT NULL,
    uploaded_by text,
    status text NOT NULL,
    issue_count integer NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS ix_evidence_uploads_tenant_document
    ON evidence_uploads (tenant_id, document_id);

INSERT INTO evidence_uploads (
    document_id,
    asset_id,
    tenant_id,
    file_name,
    stored_file_name,
    record_count,
    uploaded_at,
    uploaded_by,
    status,
    issue_count
)
VALUES (
    '7f5369d94f1742da9e34f1979bd6342a',
    'sample-import',
    'local-preview',
    'preview-assets.csv',
    'preview-assets.csv',
    0,
    now(),
    'local-development',
    'Uploaded',
    0
)
ON CONFLICT (document_id) DO UPDATE SET
    tenant_id = EXCLUDED.tenant_id,
    file_name = EXCLUDED.file_name,
    stored_file_name = EXCLUDED.stored_file_name,
    uploaded_at = EXCLUDED.uploaded_at;
