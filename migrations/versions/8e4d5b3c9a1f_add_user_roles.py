"""add authenticated user roles without affecting existing tenant ownership

Revision ID: 8e4d5b3c9a1f
Revises: 5c1b50706773
"""
from alembic import op
import sqlalchemy as sa

revision = '8e4d5b3c9a1f'
down_revision = '5c1b50706773'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    user_cols = [c['name'] for c in inspector.get_columns('users')]
    if 'role' not in user_cols:
        with op.batch_alter_table('users') as batch:
            batch.add_column(sa.Column('role', sa.String(length=20), nullable=True))
        op.execute("UPDATE users SET role = 'organizer' WHERE role IS NULL")
        with op.batch_alter_table('users') as batch:
            batch.alter_column('role', existing_type=sa.String(length=20), nullable=False, server_default='organizer')

    user_indexes = [idx['name'] for idx in inspector.get_indexes('users')]
    if 'ix_users_role' not in user_indexes:
        with op.batch_alter_table('users') as batch:
            batch.create_index('ix_users_role', ['role'])

    event_indexes = [idx['name'] for idx in inspector.get_indexes('events')]
    if 'ix_events_user_id' not in event_indexes:
        with op.batch_alter_table('events') as batch:
            batch.create_index('ix_events_user_id', ['user_id'])


def downgrade():
    with op.batch_alter_table('events') as batch:
        batch.drop_index('ix_events_user_id')
    with op.batch_alter_table('users') as batch:
        batch.drop_index('ix_users_role')
        batch.drop_column('role')
