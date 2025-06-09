"""Rename tx_hash and add payment_tx_id + method

Revision ID: a4c372191c00
Revises: 7bc53494601a
Create Date: 2025-05-26 20:27:42.299469

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a4c372191c00'
down_revision: Union[str, None] = '7bc53494601a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename 'tx_hash' to 'sct_tx_hash'
    op.alter_column('token_purchases', 'tx_hash', new_column_name='sct_tx_hash')
    
    # Rename 'tx_hash' to 'sct_tx_hash'
    op.alter_column('token_purchases', 'amount_stc', new_column_name='amount_sct')

    # Add new column for Mpesa or STRK transaction hash
    op.add_column('token_purchases', sa.Column('payment_tx_id', sa.String(length=255), nullable=True))

    # Copy existing values (optional, if STRK tx == previous tx)
    op.execute("UPDATE token_purchases SET payment_tx_id = sct_tx_hash")

    # Set NOT NULL after migration fills values
    op.alter_column('token_purchases', 'payment_tx_id', nullable=False)

    # Add payment_method: strk, mpesa, etc.
    op.add_column('token_purchases', sa.Column('payment_method', sa.String(length=20), nullable=False, server_default='strk'))

def downgrade() -> None:
    op.drop_column('token_purchases', 'payment_method')
    op.drop_column('token_purchases', 'payment_tx_id')
    op.alter_column('token_purchases', 'sct_tx_hash', new_column_name='tx_hash')
