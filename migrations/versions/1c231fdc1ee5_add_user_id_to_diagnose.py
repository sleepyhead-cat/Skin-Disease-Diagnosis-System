"""Add user_id to Diagnose

Revision ID: 1c231fdc1ee5
Revises: 8f9fa44ba2ab
Create Date: 2026-02-09 15:21:55.901811

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1c231fdc1ee5'
down_revision = '8f9fa44ba2ab'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('diagnoses', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('diagnosed_at', sa.DateTime(), nullable=False))

        # Explicitly name the foreign key constraint
        batch_op.create_foreign_key(
            'fk_diagnoses_user_id',   # <-- name required
            'users',                  # target table
            ['user_id'],              # local column
            ['id']                    # remote column
        )

    with op.batch_alter_table('rules', schema=None) as batch_op:
        batch_op.drop_column('certainty')


def downgrade():
    with op.batch_alter_table('rules', schema=None) as batch_op:
        batch_op.add_column(sa.Column('certainty', sa.Numeric(5, 2), nullable=True))

    with op.batch_alter_table('diagnoses', schema=None) as batch_op:
        batch_op.drop_constraint('fk_diagnoses_user_id', type_='foreignkey')
        batch_op.drop_column('user_id')
        batch_op.drop_column('diagnosed_at')