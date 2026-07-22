from app.models import Review, db

def test_successful_review_submission(client, sample_event):
    response = client.post(f'/review/{sample_event.unique_code}/submit', data={
        'reviewer_name': 'Alice Smith',
        'reviewer_email': 'alice@example.com',
        'star_rating': 5,
        'review_text': 'Amazing event!',
        'attendee_type': 'First-time attendee',
        'great_sound': True,
        'would_recommend': True
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'submitted successfully' in response.data or b'Thank You' in response.data

    review = Review.query.filter_by(reviewer_email='alice@example.com').first()
    assert review is not None
    assert review.star_rating == 5
    assert review.event_id == sample_event.id
    assert 'Great Sound' in review.get_categories()

def test_duplicate_email_review_rejection(client, sample_event):
    # First submission
    client.post(f'/review/{sample_event.unique_code}/submit', data={
        'reviewer_name': 'Bob Jones',
        'reviewer_email': 'bob@example.com',
        'star_rating': 4,
        'review_text': 'Good event.'
    })

    # Second submission with same email for same event
    response = client.post(f'/review/{sample_event.unique_code}/submit', data={
        'reviewer_name': 'Bob Jones',
        'reviewer_email': 'bob@example.com',
        'star_rating': 1,
        'review_text': 'Changed my mind.'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Thank You' in response.data


    # Verify only one review exists
    reviews = Review.query.filter_by(event_id=sample_event.id, reviewer_email='bob@example.com').all()
    assert len(reviews) == 1
    assert reviews[0].star_rating == 4

def test_review_rejection_when_allow_reviews_false(client, sample_event):
    sample_event.allow_reviews = False
    db.session.commit()

    # GET review form
    get_resp = client.get(f'/review/{sample_event.unique_code}')
    assert get_resp.status_code == 200
    assert b'Reviews Disabled' in get_resp.data or b'not accepting' in get_resp.data or b'disabled' in get_resp.data.lower()

    # POST submission
    post_resp = client.post(f'/review/{sample_event.unique_code}/submit', data={
        'reviewer_name': 'Charlie',
        'reviewer_email': 'charlie@example.com',
        'star_rating': 5
    }, follow_redirects=True)

    assert post_resp.status_code == 200
    assert b'Reviews are not allowed' in post_resp.data

    assert Review.query.filter_by(reviewer_email='charlie@example.com').first() is None

def test_invalid_star_rating_rejected(client, sample_event):
    # Star rating < 1
    resp_low = client.post(f'/review/{sample_event.unique_code}/submit', data={
        'reviewer_name': 'Dave',
        'reviewer_email': 'dave@example.com',
        'star_rating': 0,
        'review_text': 'Bad rating value'
    })
    assert resp_low.status_code == 200
    assert Review.query.filter_by(reviewer_email='dave@example.com').first() is None

    # Star rating > 5
    resp_high = client.post(f'/review/{sample_event.unique_code}/submit', data={
        'reviewer_name': 'Eve',
        'reviewer_email': 'eve@example.com',
        'star_rating': 6,
        'review_text': 'Invalid rating value'
    })
    assert resp_high.status_code == 200
    assert Review.query.filter_by(reviewer_email='eve@example.com').first() is None
