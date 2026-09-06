"""add analysis checkpoint

Revision ID: 62c8fe5d11b2
Revises: 2874806da0ef
Create Date: 2026-09-06
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "62c8fe5d11b2"
down_revision: Union[str, Sequence[str], None] = "2874806da0ef"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    with op.batch_alter_table("analysis_runs") as batch_op:
        batch_op.add_column(sa.Column("last_completed_stage", sa.String(length=20), nullable=True))
        batch_op.create_check_constraint(
            "ck_analysis_runs_analysis_checkpoint_valid",
            "last_completed_stage IS NULL OR last_completed_stage IN ('scraping', 'analyzing', 'generating')",
        )

def downgrade() -> None:
    with op.batch_alter_table("analysis_runs") as batch_op:
        batch_op.drop_constraint("ck_analysis_runs_analysis_checkpoint_valid", type_="check")
        batch_op.drop_column("last_completed_stage")
