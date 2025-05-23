"""Added devices table

Revision ID: 842ad071c022
Revises: 69da158c27d8
Create Date: 2025-05-17 17:21:25.990814

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '842ad071c022'
down_revision: Union[str, None] = '69da158c27d8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('devices',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('device_type', sa.String(length=50), nullable=False),
    sa.Column('device_id', sa.String(length=50), nullable=False),
    sa.Column('connection_type', sa.String(length=50), nullable=False),
    sa.Column('status', sa.String(length=50), nullable=True),
    sa.Column('pin_loads', sa.JSON(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('device_id')
    )
    op.create_index(op.f('ix_devices_id'), 'devices', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_devices_id'), table_name='devices')
    op.drop_table('devices')
    # ### end Alembic commands ###
