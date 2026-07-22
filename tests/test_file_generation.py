import os
from app.models import Review, db

def login_as(client, user):
    client.post('/auth/login', data={
        'username': user.username,
        'password': 'Password123!'
    })

def test_qr_code_generation_in_memory(client, organizer_user, sample_event):
    login_as(client, organizer_user)

    qr_dir = os.path.join(os.path.dirname(__file__), '..', 'app', 'static', 'qr_codes')
    if os.path.exists(qr_dir):
        initial_files = set(os.listdir(qr_dir))
    else:
        initial_files = set()

    response = client.get(f'/event/{sample_event.id}/qr')
    assert response.status_code == 200
    assert response.mimetype in ('image/png', 'application/octet-stream')
    assert len(response.data) > 0
    # Magic numbers for PNG files
    assert response.data.startswith(b'\x89PNG\r\n\x1a\n')

    if os.path.exists(qr_dir):
        current_files = set(os.listdir(qr_dir))
        assert current_files == initial_files

def test_csv_export_in_memory(client, organizer_user, sample_event):
    login_as(client, organizer_user)

    # Add a review to export
    review = Review(
        event_id=sample_event.id,
        reviewer_name='Tester',
        reviewer_email='tester@example.com',
        star_rating=5,
        review_text='Exportable review text'
    )
    db.session.add(review)
    db.session.commit()

    exports_dir = os.path.join(os.path.dirname(__file__), '..', 'app', 'static', 'exports')
    if os.path.exists(exports_dir):
        initial_files = set(os.listdir(exports_dir))
    else:
        initial_files = set()

    response = client.get(f'/event/{sample_event.id}/export')
    assert response.status_code == 200
    assert response.mimetype in ('text/csv', 'application/octet-stream')
    assert b'Review ID,Reviewer Name,Reviewer Email' in response.data
    assert b'Tester' in response.data
    assert b'Exportable review text' in response.data

    if os.path.exists(exports_dir):
        current_files = set(os.listdir(exports_dir))
        assert current_files == initial_files
