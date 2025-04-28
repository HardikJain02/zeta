"""Initial schema

Revision ID: 20230929_0001
Revises: 
Create Date: 2023-09-29 00:01:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20230929_0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create accounts table
    op.create_table(
        'accounts',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('account_number', sa.String(20), nullable=False, unique=True),
        sa.Column('account_name', sa.String(100), nullable=False),
        sa.Column('balance', sa.Numeric(precision=18, scale=2), nullable=False, default=0),
        sa.Column('currency', sa.String(3), nullable=False, default='USD'),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('version', sa.Integer(), nullable=False, default=1),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.CheckConstraint('balance >= 0', name='check_balance_non_negative'),
    )
    
    # Create indexes for accounts table
    op.create_index('idx_account_number', 'accounts', ['account_number'], unique=True)
    op.create_index('idx_account_number_currency', 'accounts', ['account_number', 'currency'])
    
    # Create transactions table
    op.create_table(
        'transactions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('account_id', sa.String(36), sa.ForeignKey('accounts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('transaction_type', sa.Enum('debit', 'credit', name='transactiontype'), nullable=False),
        sa.Column('amount', sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False),
        sa.Column('status', sa.Enum('pending', 'completed', 'failed', 'reversed', name='transactionstatus'), nullable=False, default='pending'),
        sa.Column('reference', sa.String(50), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('metadata', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    
    # Create indexes for transactions table
    op.create_index('idx_transaction_account_id', 'transactions', ['account_id'])
    op.create_index('idx_transaction_status', 'transactions', ['status'])
    op.create_index('idx_transaction_created_at', 'transactions', ['created_at'])
    op.create_index('idx_transaction_reference', 'transactions', ['reference'])


def downgrade():
    # Drop indexes first
    op.drop_index('idx_transaction_reference', table_name='transactions')
    op.drop_index('idx_transaction_created_at', table_name='transactions')
    op.drop_index('idx_transaction_status', table_name='transactions')
    op.drop_index('idx_transaction_account_id', table_name='transactions')
    op.drop_index('idx_account_number_currency', table_name='accounts')
    op.drop_index('idx_account_number', table_name='accounts')
    
    # Drop tables
    op.drop_table('transactions')
    
    # Drop enum types
    op.execute('DROP TYPE transactionstatus')
    op.execute('DROP TYPE transactiontype')
    
    op.drop_table('accounts') 