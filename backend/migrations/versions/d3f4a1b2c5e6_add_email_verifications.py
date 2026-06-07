"""add_email_verifications

Revision ID: d3f4a1b2c5e6
Revises: 297d9bd42267
Create Date: 2026-06-07 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'd3f4a1b2c5e6'
down_revision = '297d9bd42267'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('email_verifications',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('email', sa.String(120), nullable=False, index=True),
        sa.Column('code', sa.String(6), nullable=False),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('is_used', sa.Boolean(), default=False),
    )


def downgrade():
    op.drop_table('email_verifications')
