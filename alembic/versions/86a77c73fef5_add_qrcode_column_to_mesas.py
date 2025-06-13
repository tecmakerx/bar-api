"""add_qrcode_column_to_mesas

Revision ID: 86a77c73fef5
Revises: 
Create Date: 2025-06-13 16:32:06.919543

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '86a77c73fef5'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('mesas', sa.Column('qrcode', sa.LargeBinary, nullable=True))

def downgrade():
    op.drop_column('mesas', 'qrcode')
