"""
Alembic migration to add circular_items table.
Run with: alembic upgrade head
"""

from alembic import op
import sqlalchemy as sa
from datetime import datetime


def upgrade():
    """Add circular_items table."""
    op.create_table(
        'circular_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('retailer', sa.String(), nullable=False),
        sa.Column('item_name', sa.String(), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(), nullable=False, server_default='ea'),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('source', sa.String(), nullable=False, server_default='pdf'),
        sa.Column('valid_from', sa.Date(), nullable=True),
        sa.Column('valid_until', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add indexes for faster queries
    op.create_index('ix_circular_items_retailer', 'circular_items', ['retailer'])
    op.create_index('ix_circular_items_item_name', 'circular_items', ['item_name'])
    op.create_index('ix_circular_items_created_at', 'circular_items', ['created_at'])


def downgrade():
    """Remove circular_items table."""
    op.drop_index('ix_circular_items_created_at', table_name='circular_items')
    op.drop_index('ix_circular_items_item_name', table_name='circular_items')
    op.drop_index('ix_circular_items_retailer', table_name='circular_items')
    op.drop_table('circular_items')
