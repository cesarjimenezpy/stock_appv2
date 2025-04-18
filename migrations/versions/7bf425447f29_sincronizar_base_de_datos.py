"""Sincronizar base de datos

Revision ID: 7bf425447f29
Revises: 3cc5fd505ec6
Create Date: 2024-11-23 09:14:42.558067

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7bf425447f29'
down_revision = '3cc5fd505ec6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('cuota', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key(None, 'venta', ['venta_id'], ['id'], ondelete='CASCADE')

    with op.batch_alter_table('producto', schema=None) as batch_op:
        batch_op.add_column(sa.Column('ubicacion', sa.String(length=100), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('producto', schema=None) as batch_op:
        batch_op.drop_column('ubicacion')

    with op.batch_alter_table('cuota', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key(None, 'venta', ['venta_id'], ['id'])

    # ### end Alembic commands ###
