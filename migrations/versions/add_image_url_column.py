"""add image_url to recipe

Revision ID: (will be auto-generated)
Revises: b381b38cbac6
Create Date: (will be auto-generated)

"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('recipe', sa.Column('image_url', sa.String(length=500), nullable=True))

def downgrade():
    op.drop_column('recipe', 'image_url')