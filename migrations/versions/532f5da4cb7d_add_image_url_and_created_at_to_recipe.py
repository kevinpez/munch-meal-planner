"""Add image_url and created_at to Recipe

Revision ID: 532f5da4cb7d
Revises: 47d17cb1a147
Create Date: 2024-11-02 10:35:46.315873

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '532f5da4cb7d'
down_revision = '47d17cb1a147'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('recipe', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=True))
        batch_op.alter_column('name',
               existing_type=sa.VARCHAR(length=100),
               type_=sa.String(length=200),
               existing_nullable=False)
        batch_op.alter_column('ingredients',
               existing_type=sa.TEXT(),
               nullable=False)
        batch_op.alter_column('instructions',
               existing_type=sa.TEXT(),
               nullable=False)
        batch_op.alter_column('user_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.drop_index('ix_recipe_name')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('recipe', schema=None) as batch_op:
        batch_op.create_index('ix_recipe_name', ['name'], unique=False)
        batch_op.alter_column('user_id',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('instructions',
               existing_type=sa.TEXT(),
               nullable=True)
        batch_op.alter_column('ingredients',
               existing_type=sa.TEXT(),
               nullable=True)
        batch_op.alter_column('name',
               existing_type=sa.String(length=200),
               type_=sa.VARCHAR(length=100),
               existing_nullable=False)
        batch_op.drop_column('created_at')

    # ### end Alembic commands ###
