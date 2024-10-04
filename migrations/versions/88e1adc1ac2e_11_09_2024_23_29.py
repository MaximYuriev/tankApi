"""11.09.2024 23:29

Revision ID: 88e1adc1ac2e
Revises: e04f1155fd83
Create Date: 2024-09-11 23:29:58.477737

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '88e1adc1ac2e'
down_revision: Union[str, None] = 'e04f1155fd83'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('session_fk_user_id_fkey', 'session', type_='foreignkey')
    op.create_foreign_key(None, 'session', 'user', ['fk_user_id'], ['user_id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'session', type_='foreignkey')
    op.create_foreign_key('session_fk_user_id_fkey', 'session', 'user', ['fk_user_id'], ['user_id'])
    # ### end Alembic commands ###
