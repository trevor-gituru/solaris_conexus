"""Turn off auto increment for Device.id

Revision ID: 5d8000898cfe
Revises: 567bc6a589f5
Create Date: 2025-05-20 12:25:25.157025

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5d8000898cfe'
down_revision: Union[str, None] = '567bc6a589f5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_devices_instruction'), 'devices', ['instruction'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_devices_instruction'), table_name='devices')
    # ### end Alembic commands ###
