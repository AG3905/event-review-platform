from app.models import Review, db

def login_as(client, user):
    client.post('/auth/login', data={
        'username': user.username,
        'password': 'Password123!'
    })

def create_sample_review(event, email='reviewer@example.com'):
    review = Review(
        event_id=event.id,
        reviewer_name='Reviewer Person',
        reviewer_email=email,
        star_rating=5,
        review_text='Great event!',
        is_approved=True,
        is_featured=False
    )
    db.session.add(review)
    db.session.commit()
    return review

def test_organizer_can_moderate_own_review(client, organizer_user, sample_event):
    login_as(client, organizer_user)
    review = create_sample_review(sample_event)

    # Reject
    resp = client.post(f'/api/review/{review.id}/reject')
    assert resp.status_code == 200
    assert resp.get_json()['success'] is True
    assert Review.query.get(review.id).is_approved is False

    # Approve
    resp = client.post(f'/api/review/{review.id}/approve')
    assert resp.status_code == 200
    assert resp.get_json()['success'] is True
    assert Review.query.get(review.id).is_approved is True

    # Feature
    resp = client.post(f'/api/review/{review.id}/feature')
    assert resp.status_code == 200
    assert resp.get_json()['is_featured'] is True

    # Delete
    resp = client.delete(f'/api/review/{review.id}/delete')
    assert resp.status_code == 200
    assert Review.query.get(review.id) is None

def test_organizer_cannot_moderate_other_event_review(client, organizer_user, other_event):
    login_as(client, organizer_user)
    review = create_sample_review(other_event, email='other_reviewer@example.com')

    # Attempt reject
    resp = client.post(f'/api/review/{review.id}/reject')
    assert resp.status_code == 404
    assert Review.query.get(review.id).is_approved is True

    # Attempt delete
    resp = client.delete(f'/api/review/{review.id}/delete')
    assert resp.status_code == 404
    assert Review.query.get(review.id) is not None

def test_admin_can_moderate_any_review(client, admin_user, sample_event, other_event):
    login_as(client, admin_user)
    r1 = create_sample_review(sample_event, email='r1@example.com')
    r2 = create_sample_review(other_event, email='r2@example.com')

    # Admin rejects r1
    resp1 = client.post(f'/api/review/{r1.id}/reject')
    assert resp1.status_code == 200

    # Admin deletes r2
    resp2 = client.delete(f'/api/review/{r2.id}/delete')
    assert resp2.status_code == 200

    assert Review.query.get(r1.id).is_approved is False
    assert Review.query.get(r2.id) is None
