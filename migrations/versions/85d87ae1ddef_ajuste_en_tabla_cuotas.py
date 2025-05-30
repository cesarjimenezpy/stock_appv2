"""ajuste en tabla cuotas.

Revision ID: 85d87ae1ddef
Revises: 8d6252b3cf9b
Create Date: 2024-08-17 11:15:36.473554

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '85d87ae1ddef'
down_revision = '8d6252b3cf9b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('cuota', schema=None) as batch_op:
        batch_op.add_column(sa.Column('fecha_pago', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('cuota', schema=None) as batch_op:
        batch_op.drop_column('fecha_pago')

    # ### end Alembic commands ###
