"""Add user_id to Audit model

Revision ID: 9d6e7f8g9h0i
Revises: 8c5d6e7f8g9h
Create Date: 2026-02-03 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9d6e7f8g9h0i'
down_revision: Union[str, Sequence[str], None] = '8c5d6e7f8g9h'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add user_id foreign key to audits table"""
    
    # В новых БД колонка user_id уже есть в initial миграции, поэтому
    # добавляем constraint и заполняем данные только если необходимо.
    # Используем IF NOT EXISTS для совместимости с существующими схемами.
    op.execute(
        "ALTER TABLE audits "
        "ADD COLUMN IF NOT EXISTS user_id INTEGER"
    )

    # Добавляем foreign key constraint (если его ещё нет).
    # Alembic не имеет IF NOT EXISTS для constraint, поэтому полагаемся на то,
    # что миграция применяется один раз на чистой БД или на БД без этого constraint.
    op.create_foreign_key(
        'fk_audits_user_id',
        'audits',
        'users',
        ['user_id'],
        ['id'],
    )
    
    # Устанавливаем default для существующих аудитов (админ пользователь с ID 1),
    # если поле пустое.
    op.execute('UPDATE audits SET user_id = 1 WHERE user_id IS NULL')
    
    # Делаем поле NOT NULL после заполнения
    op.alter_column('audits', 'user_id', nullable=False, existing_type=sa.Integer())


def downgrade() -> None:
    """Remove user_id foreign key from audits table"""
    
    op.drop_constraint('fk_audits_user_id', 'audits', type_='foreignkey')
    op.drop_column('audits', 'user_id')
