"""Add image_url to Recipe model

Revision ID: add_image_url_column
Create Date: 2024-11-02
"""
from alembic import op
import sqlalchemy as sa

revision = 'add_image_url_column'
down_revision = None

def upgrade():
    op.add_column('recipe', sa.Column('image_url', sa.String(length=500), nullable=True))

def downgrade():
    op.drop_column('recipe', 'image_url') 