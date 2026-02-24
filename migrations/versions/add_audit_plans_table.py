"""Add audit_plans table

Revision ID: a1b2c3d4e5f6
Revises: 9d6e7f8g9h0i
Create Date: 2026-02-03 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '9d6e7f8g9h0i'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create audit_plans table."""
    # В актуальной initial-миграции таблица audit_plans уже создаётся.
    # Для совместимости со старыми БД используем PostgreSQL-специфичный
    # CREATE TABLE IF NOT EXISTS, чтобы избежать ошибки DuplicateTable.
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS audit_plans (
            id SERIAL PRIMARY KEY,
            device_id INTEGER NOT NULL REFERENCES devices (id),
            frequency VARCHAR(20) NOT NULL,
            next_due_date DATE NOT NULL,
            responsible_employee_id INTEGER REFERENCES employees (id)
        )
        """
    )


def downgrade() -> None:
    """Drop audit_plans table."""
    op.drop_table('audit_plans')
