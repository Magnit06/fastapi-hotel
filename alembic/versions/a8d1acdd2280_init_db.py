"""init DB

Revision ID: a8d1acdd2280
Revises: 
Create Date: 2022-02-12 15:04:44.211572

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a8d1acdd2280'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('rooms',
    sa.Column('created_at', sa.DateTime(), nullable=False, comment='Время создания записи'),
    sa.Column('updated_at', sa.DateTime(), nullable=False, comment='Время последнего изменения записи'),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('price', sa.DECIMAL(), nullable=False, comment='Цена за ночь'),
    sa.Column('name', sa.Integer(), nullable=False, comment='Номер комнаты'),
    sa.Column('number_of_seats', sa.SmallInteger(), nullable=False, comment='количество мест'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_rooms_created_at'), 'rooms', ['created_at'], unique=False)
    op.create_index(op.f('ix_rooms_id'), 'rooms', ['id'], unique=False)
    op.create_index(op.f('ix_rooms_updated_at'), 'rooms', ['updated_at'], unique=False)
    op.create_table('users',
    sa.Column('created_at', sa.DateTime(), nullable=False, comment='Время создания записи'),
    sa.Column('updated_at', sa.DateTime(), nullable=False, comment='Время последнего изменения записи'),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('login', sa.String(length=20), nullable=False, comment='Логин пользователя'),
    sa.Column('password', sa.Unicode(length=60), nullable=False, comment='Пароль пользователя'),
    sa.Column('role', postgresql.ENUM('A', 'M', name='Роль'), nullable=False, comment='Роль пользователя'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('login')
    )
    op.create_index(op.f('ix_users_created_at'), 'users', ['created_at'], unique=False)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_updated_at'), 'users', ['updated_at'], unique=False)
    op.create_table('booking_numbers',
    sa.Column('created_at', sa.DateTime(), nullable=False, comment='Время создания записи'),
    sa.Column('updated_at', sa.DateTime(), nullable=False, comment='Время последнего изменения записи'),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('booking_number', postgresql.UUID(as_uuid=True), nullable=False, comment='Номер брони'),
    sa.Column('date_in', sa.Date(), nullable=False, comment='Дата заезда'),
    sa.Column('date_out', sa.Date(), nullable=False, comment='Дата выезда'),
    sa.Column('room_id', sa.Integer(), nullable=True, comment='Внешний ключ к комнатам'),
    sa.ForeignKeyConstraint(['room_id'], ['rooms.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('booking_number')
    )
    op.create_index(op.f('ix_booking_numbers_created_at'), 'booking_numbers', ['created_at'], unique=False)
    op.create_index(op.f('ix_booking_numbers_id'), 'booking_numbers', ['id'], unique=False)
    op.create_index(op.f('ix_booking_numbers_updated_at'), 'booking_numbers', ['updated_at'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_booking_numbers_updated_at'), table_name='booking_numbers')
    op.drop_index(op.f('ix_booking_numbers_id'), table_name='booking_numbers')
    op.drop_index(op.f('ix_booking_numbers_created_at'), table_name='booking_numbers')
    op.drop_table('booking_numbers')
    op.drop_index(op.f('ix_users_updated_at'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_created_at'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_rooms_updated_at'), table_name='rooms')
    op.drop_index(op.f('ix_rooms_id'), table_name='rooms')
    op.drop_index(op.f('ix_rooms_created_at'), table_name='rooms')
    op.drop_table('rooms')
    # ### end Alembic commands ###
