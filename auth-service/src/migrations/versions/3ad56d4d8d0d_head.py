"""head

Revision ID: 3ad56d4d8d0d
Revises: d07244dddb53
Create Date: 2024-02-13 23:09:27.060820

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '3ad56d4d8d0d'
down_revision: Union[str, None] = 'd07244dddb53'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
