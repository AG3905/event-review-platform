import csv
import io
from app.models import EventQuestion, Review, ReviewAnswer, db
from app.utils import export_reviews_csv


def test_csv_export_includes_dynamic_questions_and_location(app, sample_event):
    q1 = EventQuestion(event_id=sample_event.id, question_text='Custom Question 1', question_type='rating', is_active=True)
    db.session.add(q1)
    db.session.commit()

    rev = Review(
        event_id=sample_event.id,
        reviewer_name='Charlie',
        reviewer_email='charlie@example.com',
        reviewer_town='Denver',
        reviewer_state='CO',
        star_rating=5,
        review_text='Awesome',
        is_approved=True
    )
    db.session.add(rev)
    db.session.commit()

    ans = ReviewAnswer(review_id=rev.id, question_id=q1.id, answer_text='5')
    db.session.add(ans)
    db.session.commit()

    csv_buf = export_reviews_csv(sample_event)
    content = csv_buf.getvalue().decode('utf-8')
    reader = csv.reader(io.StringIO(content))
    rows = list(reader)

    header = rows[0]
    assert 'Reviewer Town' in header
    assert 'Reviewer State' in header
    assert 'Custom Question 1' in header

    data_row = rows[1]
    town_idx = header.index('Reviewer Town')
    state_idx = header.index('Reviewer State')
    q_idx = header.index('Custom Question 1')

    assert data_row[town_idx] == 'Denver'
    assert data_row[state_idx] == 'CO'
    assert data_row[q_idx] == '5'
