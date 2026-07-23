"""dynamic questions and location fields

Revision ID: 9a5e2f1b8c3d
Revises: 8e4d5b3c9a1f
"""
from alembic import op
import sqlalchemy as sa
import json

revision = '9a5e2f1b8c3d'
down_revision = '8e4d5b3c9a1f'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table('event_questions'):
        op.create_table(
            'event_questions',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('event_id', sa.Integer(), nullable=False),
            sa.Column('question_text', sa.String(length=300), nullable=False),
            sa.Column('question_type', sa.String(length=20), nullable=False),
            sa.Column('options', sa.Text(), nullable=True),
            sa.Column('is_required', sa.Boolean(), nullable=True, server_default=sa.text('false')),
            sa.Column('display_order', sa.Integer(), nullable=True, server_default='0'),
            sa.Column('is_active', sa.Boolean(), nullable=True, server_default=sa.text('true')),
            sa.ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('ix_event_questions_event_id', 'event_questions', ['event_id'], unique=False)

    if not inspector.has_table('review_answers'):
        op.create_table(
            'review_answers',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('review_id', sa.Integer(), nullable=False),
            sa.Column('question_id', sa.Integer(), nullable=False),
            sa.Column('answer_text', sa.Text(), nullable=True),
            sa.ForeignKeyConstraint(['question_id'], ['event_questions.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['review_id'], ['reviews.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('ix_review_answers_question_id', 'review_answers', ['question_id'], unique=False)
        op.create_index('ix_review_answers_review_id', 'review_answers', ['review_id'], unique=False)

    if not inspector.has_table('saved_question_sets'):
        op.create_table(
            'saved_question_sets',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('organizer_id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=100), nullable=False),
            sa.Column('questions', sa.Text(), nullable=True),
            sa.ForeignKeyConstraint(['organizer_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('ix_saved_question_sets_organizer_id', 'saved_question_sets', ['organizer_id'], unique=False)

    event_cols = [c['name'] for c in inspector.get_columns('events')]
    with op.batch_alter_table('events') as batch:
        if 'is_custom_category' not in event_cols:
            batch.add_column(sa.Column('is_custom_category', sa.Boolean(), nullable=True, server_default=sa.text('false')))
        if 'allow_location_questions' not in event_cols:
            batch.add_column(sa.Column('allow_location_questions', sa.Boolean(), nullable=True, server_default=sa.text('true')))

    review_cols = [c['name'] for c in inspector.get_columns('reviews')]
    with op.batch_alter_table('reviews') as batch:
        if 'reviewer_town' not in review_cols:
            batch.add_column(sa.Column('reviewer_town', sa.String(length=100), nullable=True))
        if 'reviewer_state' not in review_cols:
            batch.add_column(sa.Column('reviewer_state', sa.String(length=100), nullable=True))

    bind = op.get_bind()
    events = bind.execute(sa.text("SELECT id FROM events")).fetchall()
    legacy_keys = [
        ('Great Sound', 'yes_no'),
        ('Good Venue', 'yes_no'),
        ('Worth the Price', 'yes_no'),
        ('Well Organized', 'yes_no')
    ]
    for ev in events:
        event_id = ev[0]
        q_ids = {}
        for idx, (q_text, q_type) in enumerate(legacy_keys):
            res = bind.execute(sa.text(
                "INSERT INTO event_questions (event_id, question_text, question_type, is_required, display_order, is_active) "
                "VALUES (:event_id, :q_text, :q_type, :is_req, :idx, :is_act) RETURNING id"
            ), {"event_id": event_id, "q_text": q_text, "q_type": q_type, "is_req": False, "idx": idx, "is_act": True})
            row = res.fetchone()
            q_id = row[0] if row else None
            q_ids[q_text] = q_id

        reviews = bind.execute(sa.text(
            "SELECT id, review_categories FROM reviews WHERE event_id = :event_id"
        ), {"event_id": event_id}).fetchall()

        for r in reviews:
            r_id = r[0]
            cat_json = r[1]
            cats = json.loads(cat_json) if cat_json else []
            for q_text in q_ids:
                if q_ids[q_text]:
                    ans_val = "Yes" if q_text in cats else "No"
                    bind.execute(sa.text(
                        "INSERT INTO review_answers (review_id, question_id, answer_text) "
                        "VALUES (:review_id, :question_id, :answer_text)"
                    ), {"review_id": r_id, "question_id": q_ids[q_text], "answer_text": ans_val})


def downgrade():
    with op.batch_alter_table('reviews') as batch:
        batch.drop_column('reviewer_state')
        batch.drop_column('reviewer_town')

    with op.batch_alter_table('events') as batch:
        batch.drop_column('allow_location_questions')
        batch.drop_column('is_custom_category')

    op.drop_index('ix_saved_question_sets_organizer_id', table_name='saved_question_sets')
    op.drop_table('saved_question_sets')

    op.drop_index('ix_review_answers_review_id', table_name='review_answers')
    op.drop_index('ix_review_answers_question_id', table_name='review_answers')
    op.drop_table('review_answers')

    op.drop_index('ix_event_questions_event_id', table_name='event_questions')
    op.drop_table('event_questions')

