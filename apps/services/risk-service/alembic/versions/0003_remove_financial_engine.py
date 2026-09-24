"""Remove financial-engine persistence."""

from alembic import op


revision = "0003_remove_financial_engine"
down_revision = "0002_tenant_records_and_roi_link"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_index(
        "ix_financial_risk_evaluation",
        table_name="financial_evaluations",
    )
    op.drop_index(
        "ix_financial_asset_time",
        table_name="financial_evaluations",
    )
    op.drop_table("financial_evaluations")


def downgrade() -> None:
    raise RuntimeError(
        "The financial engine was removed; restore its migration before downgrade."
    )
