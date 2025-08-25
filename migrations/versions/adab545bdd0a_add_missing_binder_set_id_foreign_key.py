"""Add missing binder.set_id foreign key

Revision ID: adab545bdd0a
Revises: 8bbbf36329b9
Create Date: 2025-08-25 16:31:55.971401

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'adab545bdd0a'
down_revision = '8bbbf36329b9'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("binders", schema=None) as batch_op:
        batch_op.create_foreign_key(
            "fk_binders_set_id",
            "sets",
            ["set_id"],
            ["id"]
        )

def downgrade():
    with op.batch_alter_table("binders", schema=None) as batch_op:
        batch_op.drop_constraint("fk_binders_set_id", type_="foreignkey")
