"""Rename tx_hash to tx_data for TradeRequests

Revision ID: ebc11cd3a8ae
Revises: a4c372191c00
Create Date: 2025-05-26 21:33:27.956747

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'ebc11cd3a8ae'
down_revision: Union[str, None] = 'a4c372191c00'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



# If your old column is String and new is JSON
def upgrade():
    op.alter_column('trade_requests', 'stc_offered', new_column_name='sct_offered')

    # 1. Add new JSON column
    op.add_column("trade_requests", sa.Column("tx_data", sa.JSON(), nullable=True))

    # 2. Copy old tx_hash values into tx_data['create']
    op.execute("""
        UPDATE trade_requests
        SET tx_data = json_build_object('create', tx_hash)
        WHERE tx_hash IS NOT NULL
    """)

    # 3. Drop old column
    op.drop_column("trade_requests", "tx_hash")


def downgrade():
    # 1. Recreate old column
    op.add_column("trade_requests", sa.Column("tx_hash", sa.String(length=255), nullable=True))

    # 2. Restore tx_hash from tx_data['create']
    op.execute("""
        UPDATE trade_requests
        SET tx_hash = tx_data->>'create'
        WHERE tx_data IS NOT NULL AND tx_data ? 'create'
    """)

    # 3. Drop tx_data column
    op.drop_column("trade_requests", "tx_data")

    # 4. Rename sct_offered → stc_offered back
    op.alter_column('trade_requests', 'sct_offered', new_column_name='stc_offered')
