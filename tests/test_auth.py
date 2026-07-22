import os
from app.models import User, db

def test_registration_success(client):
    response = client.post('/auth/register', data={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'full_name': 'New User',
        'organization': 'New Org',
        'password': 'Password123!',
        'password2': 'Password123!'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Congratulations, you are now registered!' in response.data

    user = User.query.filter_by(username='newuser').first()
    assert user is not None
    assert user.email == 'newuser@example.com'
    assert user.role == 'organizer'

def test_registration_duplicate_username(client, organizer_user):
    response = client.post('/auth/register', data={
        'username': organizer_user.username,
        'email': 'different@example.com',
        'full_name': 'Another User',
        'organization': 'Org',
        'password': 'Password123!',
        'password2': 'Password123!'
    })
    assert response.status_code == 200
    assert b'Username already exists' in response.data

def test_registration_duplicate_email(client, organizer_user):
    response = client.post('/auth/register', data={
        'username': 'differentuser',
        'email': organizer_user.email,
        'full_name': 'Another User',
        'organization': 'Org',
        'password': 'Password123!',
        'password2': 'Password123!'
    })
    assert response.status_code == 200
    assert b'Email already registered' in response.data

def test_login_success(client, organizer_user):
    response = client.post('/auth/login', data={
        'username': organizer_user.username,
        'password': 'Password123!'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Welcome back, Organizer One!' in response.data

def test_login_bad_password(client, organizer_user):
    response = client.post('/auth/login', data={
        'username': organizer_user.username,
        'password': 'WrongPassword!'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid username or password' in response.data

def test_logout(client, organizer_user):
    # Log in first
    client.post('/auth/login', data={
        'username': organizer_user.username,
        'password': 'Password123!'
    })
    response = client.get('/auth/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'You have been logged out.' in response.data

def test_platform_admin_email_auto_promotion(client, monkeypatch):
    # Create an organizer user with admin email
    admin_email = 'adminperson@example.com'
    monkeypatch.setenv('PLATFORM_ADMIN_EMAIL', admin_email)

    user = User(
        username='futureadmin',
        email=admin_email,
        full_name='Future Admin',
        role='organizer'
    )
    user.set_password('Password123!')
    db.session.add(user)
    db.session.commit()

    assert user.role == 'organizer'

    # Log in
    client.post('/auth/login', data={
        'username': 'futureadmin',
        'password': 'Password123!'
    })

    # User should now be promoted to admin
    updated_user = User.query.filter_by(username='futureadmin').first()
    assert updated_user.role == 'admin'
    assert updated_user.is_platform_admin is True
