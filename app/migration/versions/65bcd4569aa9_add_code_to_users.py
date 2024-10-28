"""Add code to users

Revision ID: 65bcd4569aa9
Revises: 7c117d5316c2
Create Date: 2024-10-28 10:20:07.440858

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '65bcd4569aa9'
down_revision: Union[str, None] = '7c117d5316c2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('code', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'code')
    # ### end Alembic commands ###
