from app.models import Event, db

def login_as(client, user):
    client.post('/auth/login', data={
        'username': user.username,
        'password': 'Password123!'
    })

def test_organizer_cannot_view_other_event(client, organizer_user, other_event):
    login_as(client, organizer_user)
    response = client.get(f'/event/{other_event.id}')
    assert response.status_code == 404

def test_organizer_cannot_edit_other_event(client, organizer_user, other_event):
    login_as(client, organizer_user)
    response = client.get(f'/event/{other_event.id}/edit')
    assert response.status_code == 404

    post_resp = client.post(f'/event/{other_event.id}/edit', data={
        'title': 'Hacked Title',
        'category': 'Comedy',
        'venue': 'Venue',
        'event_date': '2026-12-05',
        'status': 'upcoming'
    })
    assert post_resp.status_code == 404

def test_organizer_cannot_delete_other_event(client, organizer_user, other_event):
    login_as(client, organizer_user)
    response = client.post(f'/event/{other_event.id}/delete')
    assert response.status_code == 404
    assert Event.query.get(other_event.id) is not None

def test_organizer_cannot_export_other_event(client, organizer_user, other_event):
    login_as(client, organizer_user)
    response = client.get(f'/event/{other_event.id}/export')
    assert response.status_code == 404

def test_organizer_cannot_access_admin_routes(client, organizer_user):
    login_as(client, organizer_user)

    routes = ['/admin', '/admin/organizers', '/admin/events', '/admin/reviews', '/admin/analytics']
    for r in routes:
        response = client.get(r)
        assert response.status_code == 403

def test_admin_cannot_access_organizer_only_routes(client, admin_user, sample_event):
    login_as(client, admin_user)

    # Organizer-only routes use @organizer_required decorator which checks role == 'organizer'
    organizer_routes = ['/create-event', f'/event/{sample_event.id}', f'/event/{sample_event.id}/edit', '/reviews', '/analytics']
    for r in organizer_routes:
        response = client.get(r)
        assert response.status_code == 403
