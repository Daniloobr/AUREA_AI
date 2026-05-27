"""initial_schema

Revision ID: 297d9bd42267
Revises: 
Create Date: 2026-05-27 02:42:30.764248

"""
from alembic import op
import sqlalchemy as sa


revision = '297d9bd42267'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('email', sa.String(120), nullable=False, unique=True, index=True),
        sa.Column('password_hash', sa.String(128), nullable=False),
        sa.Column('credits_balance', sa.Integer(), default=0),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('cpf', sa.String(14), nullable=True),
        sa.Column('asaas_customer_id', sa.String(50), nullable=True),
        sa.Column('is_admin', sa.Boolean(), default=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
    )

    op.create_table('password_reset_tokens',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('token', sa.String(100), unique=True, nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('used', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
    )

    op.create_table('transactions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('type', sa.String(50)),
        sa.Column('amount', sa.Integer()),
        sa.Column('balance_before', sa.Integer()),
        sa.Column('balance_after', sa.Integer()),
        sa.Column('description', sa.String(255)),
        sa.Column('status', sa.String(20), default='completed'),
        sa.Column('external_id', sa.String(100), nullable=True, unique=True),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
    )

    op.create_table('generation_jobs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('status', sa.String(20), default='queued'),
        sa.Column('tipo_ensaio', sa.String(50)),
        sa.Column('input_image_url', sa.String(500)),
        sa.Column('progress', sa.Integer(), default=0),
        sa.Column('message', sa.String(200)),
        sa.Column('error', sa.Text()),
        sa.Column('cost_moedas', sa.Integer(), default=25),
        sa.Column('images_json', sa.Text(), default='[]'),
        sa.Column('metadata_json', sa.Text(), default='{}'),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
    )


def downgrade():
    op.drop_table('generation_jobs')
    op.drop_table('transactions')
    op.drop_table('password_reset_tokens')
    op.drop_table('users')
