"""messed with set and binder model and seeder

Revision ID: 6d2c4cdfbc94
Revises: d498a351e9dc
Create Date: 2025-08-24 18:02:00.058110

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6d2c4cdfbc94'
down_revision = 'd498a351e9dc'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('binders', schema=None) as batch_op:
        batch_op.drop_column('set_name')
        batch_op.drop_column('set_logo')
        batch_op.drop_column('set_symbol')
        batch_op.drop_column('printed_total')
        batch_op.drop_column('total_in_set')
        # ❌ do NOT try to re-add set_id here

def downgrade():
    with op.batch_alter_table('binders', schema=None) as batch_op:
        batch_op.add_column(sa.Column('set_name', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('set_logo', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('set_symbol', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('printed_total', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('total_in_set', sa.Integer(), nullable=True))
