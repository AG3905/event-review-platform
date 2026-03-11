"""Seed script to create demo user(s) and sample data for interviews.

Usage:
    python scripts/seed_demo.py

It reads optional env vars:
  DEMO_USERNAME, DEMO_EMAIL, DEMO_PASSWORD

Be careful when running against production databases.
"""
from app import create_app, db
from app.models import User, Event
import os
import sys
from datetime import date


def create_demo_user(username, email, password):
    existing = User.query.filter_by(username=username).first()
    if existing:
        print(f"Demo user '{username}' already exists (id={existing.id}).")
        return existing

    user = User(username=username, email=email, full_name='Demo User')
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    print(f"Created demo user '{username}' (id={user.id}).")
    return user


def create_demo_event(user):
    ev = Event(
        user_id=user.id,
        title='Demo Event',
        category='Workshop',
        description='This is a demo event used for interview showcase.',
        venue='Demo Hall',
        event_date=date.today(),
        capacity=100
    )
    db.session.add(ev)
    db.session.commit()
    print(f"Created demo event '{ev.title}' (id={ev.id}).")
    return ev


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        username = os.environ.get('DEMO_USERNAME', 'demo_user')
        email = os.environ.get('DEMO_EMAIL', 'demo@example.com')
        password = os.environ.get('DEMO_PASSWORD', 'DemoPass123')

        # Create tables if database is empty (useful for sqlite demos)
        try:
            db.create_all()
        except Exception as e:
            print('Warning: create_all() failed — ensure migrations are applied in production. Error:', e)

        user = create_demo_user(username, email, password)
        # Optionally create a demo event (only if user has no events)
        if not user.events:
            create_demo_event(user)

        print('\nDone. Demo credentials:')
        print(f'  Username: {username}')
        print(f'  Email: {email}')
        print(f'  Password: {password}')
*** End Patch