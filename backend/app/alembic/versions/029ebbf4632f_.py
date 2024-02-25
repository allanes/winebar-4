"""empty message

Revision ID: 029ebbf4632f
Revises: 17b5a07986c8
Create Date: 2024-02-24 20:52:16.854226

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '029ebbf4632f'
down_revision: Union[str, None] = '17b5a07986c8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(f"""
            INSERT INTO menues DEFAULT VALUES;
        """
    )


def downgrade() -> None:
    pass
