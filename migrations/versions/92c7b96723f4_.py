"""empty message

Revision ID: 92c7b96723f4
Revises: 51be8a66f9c9
Create Date: 2020-03-16 15:26:35.673298

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '92c7b96723f4'
down_revision = '51be8a66f9c9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('venues', sa.Column('num_upcoming_shows', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('venues', 'num_upcoming_shows')
    # ### end Alembic commands ###
