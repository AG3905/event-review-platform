import json
from app.models import Event, EventQuestion, Review, ReviewAnswer, db


def test_create_event_with_questions(client, organizer_user):
    client.post('/auth/login', data={'username': 'organizer1', 'password': 'Password123!'})
    
    questions_data = [
        {'text': 'Sound Quality', 'type': 'rating', 'required': True},
        {'text': 'Would you return?', 'type': 'yes_no', 'required': False}
    ]

    res = client.post('/create-event', data={
        'title': 'Concert 2026',
        'category': 'Music',
        'venue': 'Arena',
        'event_date': '2026-12-10',
        'questions_json': json.dumps(questions_data)
    }, follow_redirects=True)

    assert res.status_code == 200
    event = Event.query.filter_by(title='Concert 2026').first()
    assert event is not None
    assert len(event.questions) == 2
    assert event.questions[0].question_text == 'Sound Quality'
    assert event.questions[0].is_required is True


def test_question_capping_at_10(client, organizer_user, sample_event):
    client.post('/auth/login', data={'username': 'organizer1', 'password': 'Password123!'})

    eleven_questions = [{'text': f'Question {i}', 'type': 'text'} for i in range(12)]

    res = client.post(f'/event/{sample_event.id}/edit', data={
        'title': sample_event.title,
        'category': 'Conference',
        'venue': sample_event.venue,
        'event_date': '2026-12-01',
        'status': 'upcoming',
        'allow_reviews': 'y',
        'questions_json': json.dumps(eleven_questions)
    }, follow_redirects=True)

    assert res.status_code == 200
    active_qs = EventQuestion.query.filter_by(event_id=sample_event.id, is_active=True).all()
    assert len(active_qs) == 10


def test_edit_questions_preserve_answers(client, organizer_user, sample_event):
    # Add a question
    q1 = EventQuestion(event_id=sample_event.id, question_text='Initial Q', question_type='rating', is_active=True)
    db.session.add(q1)
    db.session.commit()

    # Add a review and answer
    rev = Review(
        event_id=sample_event.id, reviewer_name='Alice', reviewer_email='alice@example.com', star_rating=5
    )
    db.session.add(rev)
    db.session.commit()

    ans = ReviewAnswer(review_id=rev.id, question_id=q1.id, answer_text='5')
    db.session.add(ans)
    db.session.commit()

    # Edit event questions - omit q1 so it soft-deactivates
    client.post('/auth/login', data={'username': 'organizer1', 'password': 'Password123!'})
    new_qs = [{'text': 'New Q', 'type': 'text'}]
    client.post(f'/event/{sample_event.id}/edit', data={
        'title': sample_event.title,
        'category': 'Conference',
        'venue': sample_event.venue,
        'event_date': '2026-12-01',
        'status': 'upcoming',
        'allow_reviews': 'y',
        'questions_json': json.dumps(new_qs)
    }, follow_redirects=True)

    # q1 should still exist in DB as is_active = False
    q1_db = db.session.get(EventQuestion, q1.id)
    assert q1_db is not None
    assert q1_db.is_active is False
    # ReviewAnswer should still exist
    assert db.session.get(ReviewAnswer, ans.id) is not None
