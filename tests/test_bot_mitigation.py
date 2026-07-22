from app.models import Review, db

def test_honeypot_bot_submission_rejected(client, sample_event):
    response = client.post(f'/review/{sample_event.unique_code}/submit', data={
        'reviewer_name': 'Spam Bot',
        'reviewer_email': 'spambot@example.com',
        'star_rating': 5,
        'review_text': 'Buy cheap products now!',
        'website': 'http://spambot.com'  # Honeypot populated!
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'submitted successfully' in response.data or b'Thank You' in response.data

    # Verify no review was created in database
    review = Review.query.filter_by(reviewer_email='spambot@example.com').first()
    assert review is None
