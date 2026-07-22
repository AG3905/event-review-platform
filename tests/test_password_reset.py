from app.models import User, db
from app.auth.routes import generate_reset_token

def test_forgot_password_existing_email(client, organizer_user):
    response = client.post('/auth/forgot-password', data={
        'email': organizer_user.email
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'If that email exists, we sent a link' in response.data

def test_forgot_password_nonexistent_email_no_leak(client):
    response = client.post('/auth/forgot-password', data={
        'email': 'nobody@example.com'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'If that email exists, we sent a link' in response.data

def test_reset_password_valid_token(client, organizer_user):
    token = generate_reset_token(organizer_user)

    # GET reset form
    get_resp = client.get(f'/auth/reset-password/{token}')
    assert get_resp.status_code == 200
    assert b'Set New Password' in get_resp.data

    # POST new password
    post_resp = client.post(f'/auth/reset-password/{token}', data={
        'new_password': 'NewPassword123!',
        'new_password2': 'NewPassword123!'
    }, follow_redirects=True)

    assert post_resp.status_code == 200
    assert b'Your password has been reset.' in post_resp.data

    # Confirm user can log in with new password
    user = User.query.get(organizer_user.id)
    assert user.check_password('NewPassword123!') is True

def test_reset_password_invalid_or_expired_token(client):
    bad_token = 'invalid-token-string'

    response = client.get(f'/auth/reset-password/{bad_token}', follow_redirects=True)
    assert response.status_code == 200
    assert b'invalid or has expired' in response.data
