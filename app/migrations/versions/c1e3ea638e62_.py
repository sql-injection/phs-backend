"""empty message

Revision ID: c1e3ea638e62
Revises: 8a2c1aeb6dfa
Create Date: 2018-11-20 16:57:44.915538

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c1e3ea638e62'
down_revision = '8a2c1aeb6dfa'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('heart_rate', sa.Column('rr', sa.Float(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('heart_rate', 'rr')
    # ### end Alembic commands ###
