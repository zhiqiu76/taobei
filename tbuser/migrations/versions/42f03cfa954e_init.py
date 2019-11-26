"""init

Revision ID: 42f03cfa954e
Revises: 
Create Date: 2019-11-25 23:02:22.276115

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '42f03cfa954e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('username', sa.String(length=20), nullable=False),
    sa.Column('password', sa.String(length=256), nullable=False),
    sa.Column('avatar', sa.String(length=200), nullable=False),
    sa.Column('gender', sa.String(length=1), nullable=False),
    sa.Column('mobile', sa.String(length=11), nullable=True),
    sa.Column('wallet_money', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('mobile'),
    sa.UniqueConstraint('username')
    )
    op.create_table('address',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('address', sa.String(length=200), nullable=False),
    sa.Column('zip_code', sa.String(length=6), nullable=False),
    sa.Column('phone', sa.String(length=20), nullable=False),
    sa.Column('is_default', sa.Boolean(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('wallet_transaction',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('amount', sa.Integer(), nullable=False),
    sa.Column('note', sa.String(length=200), nullable=False),
    sa.Column('payer_id', sa.Integer(), nullable=False),
    sa.Column('payee_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['payee_id'], ['user.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['payer_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('wallet_transaction')
    op.drop_table('address')
    op.drop_table('user')
    # ### end Alembic commands ###
