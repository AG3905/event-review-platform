import json
from app.models import EventQuestion, Review, ReviewAnswer, db


def test_dynamic_review_submission(client, sample_event):
    q1 = EventQuestion(event_id=sample_event.id, question_text='Acoustics Rating', question_type='rating', is_required=True, is_active=True)
    q2 = EventQuestion(event_id=sample_event.id, question_text='Pace', question_type='single_choice', is_active=True)
    q2.set_options(['Slow', 'Fast'])
    db.session.add_all([q1, q2])
    db.session.commit()

    # Missing required q1 should fail validation
    res = client.post(f'/review/{sample_event.unique_code}/submit', data={
        'reviewer_name': 'Bob',
        'reviewer_email': 'bob@example.com',
        'star_rating': 5,
        'reviewer_town': 'Springfield',
        'reviewer_state': 'IL'
    })
    assert res.status_code == 200
    assert b'Please answer the required question' in res.data

    # Valid submission
    res_ok = client.post(f'/review/{sample_event.unique_code}/submit', data={
        'reviewer_name': 'Bob',
        'reviewer_email': 'bob@example.com',
        'star_rating': 5,
        f'question_{q1.id}': '4',
        f'question_{q2.id}': 'Fast',
        'reviewer_town': 'Springfield',
        'reviewer_state': 'IL'
    }, follow_redirects=True)

    assert res_ok.status_code == 200
    rev = Review.query.filter_by(event_id=sample_event.id, reviewer_email='bob@example.com').first()
    assert rev is not None
    assert rev.reviewer_town == 'Springfield'
    assert rev.reviewer_state == 'IL'

    answers = {ans.question_id: ans.answer_text for ans in rev.answers}
    assert answers[q1.id] == '4'
    assert answers[q2.id] == 'Fast'
