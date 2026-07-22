from app.models import Review, db
from datetime import datetime

def login_as(client, user):
    client.post('/auth/login', data={
        'username': user.username,
        'password': 'Password123!'
    })

def test_pagination_page_2_offset_and_out_of_range(client, sample_event):
    # Create 30 reviews for sample_event
    for i in range(30):
        review = Review(
            event_id=sample_event.id,
            reviewer_name=f'Reviewer {i}',
            reviewer_email=f'reviewer{i}@example.com',
            star_rating=5,
            is_approved=True,
            submitted_at=datetime.utcnow()
        )
        db.session.add(review)
    db.session.commit()

    # Query page 1
    resp_p1 = client.get(f'/review/{sample_event.unique_code}/browse?page=1')
    assert resp_p1.status_code == 200
    assert b'Page 1 of 2' in resp_p1.data

    # Query page 2
    resp_p2 = client.get(f'/review/{sample_event.unique_code}/browse?page=2')
    assert resp_p2.status_code == 200
    assert b'Page 2 of 2' in resp_p2.data

    # Query out of range page (page 999) - should not 500
    resp_p999 = client.get(f'/review/{sample_event.unique_code}/browse?page=999')
    assert resp_p999.status_code == 200
    assert b'No Reviews Yet' in resp_p999.data or b'Page 999' in resp_p999.data

def test_admin_events_pagination(client, admin_user):
    login_as(client, admin_user)

    resp = client.get('/admin/events?page=1')
    assert resp.status_code == 200

    resp_out = client.get('/admin/events?page=999')
    assert resp_out.status_code == 200
    assert b'No events yet' in resp_out.data or b'Page 999' in resp_out.data
