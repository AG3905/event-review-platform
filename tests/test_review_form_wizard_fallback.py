from app.models import EventQuestion, Review, db


def test_review_form_no_js_fallback_rendering_and_post(client, sample_event):
    q1 = EventQuestion(event_id=sample_event.id, question_text='Organization', question_type='text', is_active=True)
    db.session.add(q1)
    db.session.commit()

    # GET review form - verify noscript fallback element exists
    res = client.get(f'/review/{sample_event.unique_code}')
    assert res.status_code == 200
    html = res.data.decode('utf-8')
    assert '<noscript>' in html
    assert 'Submit Review' in html

    # Submit without JS (standard POST payload)
    res_post = client.post(f'/review/{sample_event.unique_code}/submit', data={
        'reviewer_name': 'NoJS User',
        'reviewer_email': 'nojs@example.com',
        'star_rating': 4,
        f'question_{q1.id}': 'Very well organized',
        'reviewer_town': 'Austin',
        'reviewer_state': 'TX'
    }, follow_redirects=True)

    assert res_post.status_code == 200
    rev = Review.query.filter_by(event_id=sample_event.id, reviewer_email='nojs@example.com').first()
    assert rev is not None
    assert rev.reviewer_name == 'NoJS User'
    assert rev.reviewer_town == 'Austin'
