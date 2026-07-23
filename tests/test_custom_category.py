from app.models import Event
from app.question_templates import suggest_questions_for, SUGGESTED_QUESTIONS


def test_other_category_requires_custom_category(client, organizer_user):
    client.post('/auth/login', data={'username': 'organizer1', 'password': 'Password123!'})

    # Other without custom_category should fail validation
    res = client.post('/create-event', data={
        'title': 'Custom Fest',
        'category': 'Other',
        'custom_category': '',
        'venue': 'Park',
        'event_date': '2026-12-15'
    })
    assert res.status_code == 200
    assert b'Please specify a custom event type' in res.data


def test_custom_category_saving(client, organizer_user):
    client.post('/auth/login', data={'username': 'organizer1', 'password': 'Password123!'})

    res = client.post('/create-event', data={
        'title': 'Wedding Gala',
        'category': 'Other',
        'custom_category': 'Wedding Reception',
        'venue': 'Hotel Ballroom',
        'event_date': '2026-12-20'
    }, follow_redirects=True)

    assert res.status_code == 200
    event = Event.query.filter_by(title='Wedding Gala').first()
    assert event is not None
    assert event.category == 'Wedding Reception'
    assert event.is_custom_category is True


def test_suggest_questions_keyword_matching():
    # Keyword "wedding reception" matches Wedding template
    wedding_qs = suggest_questions_for('wedding reception')
    assert wedding_qs == SUGGESTED_QUESTIONS['Wedding']

    # Exact match "Music"
    music_qs = suggest_questions_for('Music')
    assert music_qs == SUGGESTED_QUESTIONS['Music']

    # Nonsense input falls back to Other
    other_qs = suggest_questions_for('xyz123nonsense')
    assert other_qs == SUGGESTED_QUESTIONS['Other']
