"""create events table

Revision ID: 0001_initial
Revises:
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("city", sa.String(length=100), nullable=False),
        sa.Column("format", sa.String(length=20), nullable=False),
        sa.Column("date", sa.String(length=100), nullable=False),
        sa.Column("deadline", sa.String(length=100), nullable=True),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("link", sa.String(length=500), nullable=False),
        sa.Column("source", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_events_title", "events", ["title"])
    op.create_index("ix_events_city", "events", ["city"])
    op.create_index("ix_events_category", "events", ["category"])


def downgrade() -> None:
    op.drop_index("ix_events_category", table_name="events")
    op.drop_index("ix_events_city", table_name="events")
    op.drop_index("ix_events_title", table_name="events")
    op.drop_table("events")
