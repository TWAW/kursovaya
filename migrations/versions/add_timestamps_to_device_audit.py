"""Add timestamps to Device and Audit models

Revision ID: 8c5d6e7f8g9h
Revises: 7c4ab5ad874c
Create Date: 2026-02-03 15:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision: str = '8c5d6e7f8g9h'
down_revision: Union[str, Sequence[str], None] = '7c4ab5ad874c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add timestamps to devices and audits tables"""
    
    # В старых БД колонки могли отсутствовать — добавляем их условно.
    # В новых (с обновлённой initial-м миграцией) они уже есть, поэтому используем
    # PostgreSQL-специфичный IF NOT EXISTS, чтобы избежать ошибок дублирования.
    op.execute(
        "ALTER TABLE devices "
        "ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITHOUT TIME ZONE"
    )
    op.execute(
        "ALTER TABLE devices "
        "ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITHOUT TIME ZONE"
    )
    op.execute(
        "ALTER TABLE audits "
        "ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITHOUT TIME ZONE"
    )
    op.execute(
        "ALTER TABLE audits "
        "ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITHOUT TIME ZONE"
    )
    
    # Устанавливаем значения по умолчанию для существующих записей
    op.execute('UPDATE devices SET created_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP WHERE created_at IS NULL')
    op.execute('UPDATE audits SET created_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP WHERE created_at IS NULL')


def downgrade() -> None:
    """Remove timestamps from devices and audits tables"""
    
    op.drop_column('audits', 'updated_at')
    op.drop_column('audits', 'created_at')
    op.drop_column('devices', 'updated_at')
    op.drop_column('devices', 'created_at')
