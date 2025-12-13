"""auto migration 2025-12-13T10:37:16+00:00

Revision ID: 93fe87d39d48
Revises: 5cb3f720cb5e
Create Date: 2025-12-13 11:37:16.647636
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '93fe87d39d48'
down_revision = '5cb3f720cb5e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Define upgrade migrations."""
    pass


def downgrade() -> None:
    """Define downgrade migrations."""
    pass
