"""empty message

Revision ID: c9fa0f03cca1
Revises: b1c71bffa656
Create Date: 2018-11-30 23:27:23.095849

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'c9fa0f03cca1'
down_revision = 'b1c71bffa656'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('disease', sa.Column('notes', sa.Text(length=500), nullable=True))
    op.drop_column('disease', 'description')
    op.add_column('medication', sa.Column('notes', sa.Text(length=500), nullable=True))
    op.drop_column('medication', 'description')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('medication', sa.Column('description', mysql.TEXT(), nullable=True))
    op.drop_column('medication', 'notes')
    op.add_column('disease', sa.Column('description', mysql.TEXT(), nullable=True))
    op.drop_column('disease', 'notes')
    # ### end Alembic commands ###
