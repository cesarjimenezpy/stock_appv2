"""Initial migration.

Revision ID: c43607d78bd8
Revises: 
Create Date: 2024-08-15 19:42:54.211407

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c43607d78bd8'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('venta', schema=None) as batch_op:
        batch_op.add_column(sa.Column('entrega_inicial', sa.Float(), nullable=False))
        batch_op.add_column(sa.Column('total', sa.Float(), nullable=False))
        batch_op.alter_column('tipo_pago',
               existing_type=sa.VARCHAR(length=10),
               type_=sa.String(length=20),
               existing_nullable=False)
        batch_op.drop_column('cantidad')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('venta', schema=None) as batch_op:
        batch_op.add_column(sa.Column('cantidad', sa.INTEGER(), nullable=False))
        batch_op.alter_column('tipo_pago',
               existing_type=sa.String(length=20),
               type_=sa.VARCHAR(length=10),
               existing_nullable=False)
        batch_op.drop_column('total')
        batch_op.drop_column('entrega_inicial')

    # ### end Alembic commands ###
