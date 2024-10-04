"""02.09.2024 18:42

Revision ID: 2087fff4a572
Revises: 7f8286ff7419
Create Date: 2024-09-02 18:42:34.583896

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2087fff4a572'
down_revision: Union[str, None] = '7f8286ff7419'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('login', sa.String(), nullable=False))
    op.drop_column('user', 'username')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('username', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_column('user', 'login')
    # ### end Alembic commands ###
