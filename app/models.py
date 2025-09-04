from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, time
import json
import string
import random
from app import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100))
    organization = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    events = db.relationship('Event', backref='organizer', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def update_last_login(self):
        self.last_login = datetime.utcnow()
        db.session.commit()

    def get_event_count(self):
        return len(self.events)

    def get_total_reviews(self):
        return sum(len(event.reviews) for event in self.events)

    def get_average_rating(self):
        all_ratings = []
        for event in self.events:
            for review in event.reviews:
                all_ratings.append(review.star_rating)
        return sum(all_ratings) / len(all_ratings) if all_ratings else 0

class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    venue = db.Column(db.String(200))
    event_date = db.Column(db.Date, nullable=False)
    event_time = db.Column(db.Time)
    capacity = db.Column(db.Integer)
    status = db.Column(db.String(20), default='upcoming')
    unique_code = db.Column(db.String(10), unique=True, nullable=False)
    allow_reviews = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    reviews = db.relationship('Review', backref='event', lazy=True, cascade='all, delete-orphan')

    def __init__(self, **kwargs):
        super(Event, self).__init__(**kwargs)
        if not self.unique_code:
            self.unique_code = self.generate_unique_code()

    @staticmethod
    def generate_unique_code():
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            if not Event.query.filter_by(unique_code=code).first():
                return code

    def get_review_count(self):
        return len(self.reviews)

    def get_average_rating(self):
        ratings = [review.star_rating for review in self.reviews if review.is_approved]
        return sum(ratings) / len(ratings) if ratings else 0

    def get_rating_distribution(self):
        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for review in self.reviews:
            if review.is_approved:
                distribution[review.star_rating] += 1
        return distribution

    def get_response_rate(self):
        if self.capacity and self.capacity > 0:
            return (len(self.reviews) / self.capacity) * 100
        return 0

    def get_review_url(self):
        return f"/review/{self.unique_code}"

class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    reviewer_name = db.Column(db.String(100), nullable=False)
    reviewer_email = db.Column(db.String(100), nullable=False)
    star_rating = db.Column(db.Integer, nullable=False)
    review_text = db.Column(db.Text)
    review_categories = db.Column(db.Text)  # JSON string
    attendee_type = db.Column(db.String(50))
    would_recommend = db.Column(db.Boolean)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    is_approved = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    helpful_votes = db.Column(db.Integer, default=0)

    __table_args__ = (db.UniqueConstraint('event_id', 'reviewer_email', name='_event_reviewer_email_uc'),)

    def set_categories(self, categories_list):
        self.review_categories = json.dumps(categories_list)

    def get_categories(self):
        if self.review_categories:
            return json.loads(self.review_categories)
        return []

    def get_quality_score(self):
        score = 0
        # Base score from rating
        score += self.star_rating * 10
        # Text length bonus
        if self.review_text:
            score += min(len(self.review_text) // 10, 50)
        # Categories bonus
        score += len(self.get_categories()) * 5
        # Recommendation bonus
        if self.would_recommend:
            score += 20
        return min(score, 100)
