"""02.09.2024 18:11

Revision ID: 7f8286ff7419
Revises: 38c852ea5143
Create Date: 2024-09-02 18:11:45.347543

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7f8286ff7419'
down_revision: Union[str, None] = '38c852ea5143'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('total_score', sa.Integer(), nullable=False))
    op.add_column('user', sa.Column('total_game', sa.Integer(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'total_game')
    op.drop_column('user', 'total_score')
    # ### end Alembic commands ###
