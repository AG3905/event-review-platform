import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from datetime import date, time
from app import create_app, db
from app.models import User, Event, Review

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'RATELIMIT_ENABLED': True,
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def organizer_user(app):
    user = User(
        username='organizer1',
        email='organizer1@example.com',
        full_name='Organizer One',
        organization='Org One Inc',
        role='organizer'
    )
    user.set_password('Password123!')
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def other_organizer_user(app):
    user = User(
        username='organizer2',
        email='organizer2@example.com',
        full_name='Organizer Two',
        organization='Org Two Inc',
        role='organizer'
    )
    user.set_password('Password123!')
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def admin_user(app):
    user = User(
        username='admin1',
        email='admin1@example.com',
        full_name='Admin One',
        organization='Admin Corp',
        role='admin'
    )
    user.set_password('Password123!')
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def sample_event(app, organizer_user):
    event = Event(
        user_id=organizer_user.id,
        title='Sample Tech Conference',
        category='Conference',
        description='A test tech conference',
        venue='Main Hall',
        event_date=date(2026, 12, 1),
        event_time=time(10, 0),
        capacity=100,
        unique_code='TECH2026',
        allow_reviews=True
    )
    db.session.add(event)
    db.session.commit()
    return event

@pytest.fixture
def other_event(app, other_organizer_user):
    event = Event(
        user_id=other_organizer_user.id,
        title='Other Comedy Show',
        category='Comedy',
        description='A comedy show by organizer two',
        venue='Side Stage',
        event_date=date(2026, 12, 5),
        event_time=time(19, 0),
        capacity=50,
        unique_code='COMEDY26',
        allow_reviews=True
    )
    db.session.add(event)
    db.session.commit()
    return event
