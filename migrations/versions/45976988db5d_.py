"""empty message

Revision ID: 45976988db5d
Revises: add_image_url_column, b381b38cbac6
Create Date: 2024-11-02 09:47:35.891880

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '45976988db5d'
down_revision = ('add_image_url_column', 'b381b38cbac6')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
