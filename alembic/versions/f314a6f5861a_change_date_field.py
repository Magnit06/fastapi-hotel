"""change date field

Revision ID: f314a6f5861a
Revises: 7b50da07b177
Create Date: 2022-02-04 16:20:23.177273

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f314a6f5861a'
down_revision = '7b50da07b177'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('booking_numbers_date_in_key', 'booking_numbers', type_='unique')
    op.drop_constraint('booking_numbers_date_out_key', 'booking_numbers', type_='unique')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('booking_numbers_date_out_key', 'booking_numbers', ['date_out'])
    op.create_unique_constraint('booking_numbers_date_in_key', 'booking_numbers', ['date_in'])
    # ### end Alembic commands ###
