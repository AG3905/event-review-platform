from flask import render_template, redirect, url_for, flash, request, jsonify, send_file
from flask_login import login_required, current_user
from app.main import bp
from app.models import User, Event, Review, db
from app.forms import EventForm, ReviewForm, EditEventForm
from app.utils import generate_qr_code, export_reviews_csv
from datetime import datetime, date
from sqlalchemy import func
import os

@bp.route('/')
def index():
    return render_template('index.html', title='Event Review Platform')

@bp.route('/dashboard')
@login_required
def dashboard():
    events = current_user.events

    # Calculate dashboard statistics
    total_events = len(events)
    total_reviews = sum(len(event.reviews) for event in events)
    avg_rating = 0

    if total_reviews > 0:
        all_ratings = []
        for event in events:
            for review in event.reviews:
                if review.is_approved:
                    all_ratings.append(review.star_rating)
        avg_rating = sum(all_ratings) / len(all_ratings) if all_ratings else 0

    # Recent reviews
    recent_reviews = []
    for event in events:
        for review in event.reviews:
            if review.is_approved:
                recent_reviews.append(review)
    recent_reviews.sort(key=lambda x: x.submitted_at, reverse=True)
    recent_reviews = recent_reviews[:5]

    return render_template('dashboard/dashboard.html', title='Dashboard',
                         events=events, total_events=total_events,
                         total_reviews=total_reviews, avg_rating=avg_rating,
                         recent_reviews=recent_reviews)

@bp.route('/create-event', methods=['GET', 'POST'])
@login_required
def create_event():
    form = EventForm()
    if form.validate_on_submit():
        event = Event(
            user_id=current_user.id,
            title=form.title.data,
            category=form.category.data,
            description=form.description.data,
            venue=form.venue.data,
            event_date=form.event_date.data,
            event_time=form.event_time.data,
            capacity=form.capacity.data
        )
        db.session.add(event)
        db.session.commit()

        flash(f'Event "{event.title}" created successfully!', 'success')
        return redirect(url_for('main.event_details', event_id=event.id))

    return render_template('dashboard/create_event.html', title='Create Event', form=form)

@bp.route('/event/<int:event_id>')
@login_required
def event_details(event_id):
    event = Event.query.get_or_404(event_id)

    # Check ownership
    if event.user_id != current_user.id:
        flash('You can only view your own events.', 'error')
        return redirect(url_for('main.dashboard'))

    # Calculate statistics
    reviews = event.reviews
    approved_reviews = [r for r in reviews if r.is_approved]
    avg_rating = event.get_average_rating()
    rating_distribution = event.get_rating_distribution()
    response_rate = event.get_response_rate()

    return render_template('dashboard/event_details.html', title=f'Event: {event.title}',
                         event=event, reviews=approved_reviews, avg_rating=avg_rating,
                         rating_distribution=rating_distribution, response_rate=response_rate)

@bp.route('/event/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)

    # Check ownership
    if event.user_id != current_user.id:
        flash('You can only edit your own events.', 'error')
        return redirect(url_for('main.dashboard'))

    form = EditEventForm(obj=event)
    if form.validate_on_submit():
        form.populate_obj(event)
        event.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Event updated successfully!', 'success')
        return redirect(url_for('main.event_details', event_id=event.id))

    return render_template('dashboard/edit_event.html', title='Edit Event', form=form, event=event)

@bp.route('/event/<int:event_id>/qr')
@login_required
def event_qr_code(event_id):
    event = Event.query.get_or_404(event_id)

    # Check ownership
    if event.user_id != current_user.id:
        flash('You can only access your own events.', 'error')
        return redirect(url_for('main.dashboard'))

    # Generate QR code
    review_url = request.url_root.rstrip('/') + event.get_review_url()
    qr_path = generate_qr_code(review_url, event.unique_code)

    return send_file(qr_path, as_attachment=True, download_name=f'{event.title}_QR.png')

@bp.route('/event/<int:event_id>/export')
@login_required
def export_event_reviews(event_id):
    event = Event.query.get_or_404(event_id)

    # Check ownership
    if event.user_id != current_user.id:
        flash('You can only export your own event data.', 'error')
        return redirect(url_for('main.dashboard'))

    # Export reviews to CSV
    csv_path = export_reviews_csv(event)
    return send_file(csv_path, as_attachment=True, download_name=f'{event.title}_reviews.csv')

@bp.route('/review/<string:unique_code>')
def review_form(unique_code):
    event = Event.query.filter_by(unique_code=unique_code).first_or_404()

    if not event.allow_reviews:
        return render_template('review/reviews_disabled.html', event=event)

    form = ReviewForm()
    return render_template('review/review_form.html', title=f'Review: {event.title}',
                         event=event, form=form)

@bp.route('/review/<string:unique_code>/submit', methods=['POST'])
def submit_review(unique_code):
    event = Event.query.filter_by(unique_code=unique_code).first_or_404()

    if not event.allow_reviews:
        flash('Reviews are not allowed for this event.', 'error')
        return redirect(url_for('main.review_form', unique_code=unique_code))

    form = ReviewForm()
    if form.validate_on_submit():
        # Check if user already reviewed this event
        existing_review = Review.query.filter_by(
            event_id=event.id,
            reviewer_email=form.reviewer_email.data
        ).first()

        if existing_review:
            flash('You have already submitted a review for this event.', 'warning')
            return redirect(url_for('main.review_success', unique_code=unique_code))

        # Create review categories list
        categories = []
        if form.great_sound.data:
            categories.append('Great Sound')
        if form.good_venue.data:
            categories.append('Good Venue')
        if form.worth_price.data:
            categories.append('Worth the Price')
        if form.well_organized.data:
            categories.append('Well Organized')

        # Create review
        review = Review(
            event_id=event.id,
            reviewer_name=form.reviewer_name.data,
            reviewer_email=form.reviewer_email.data,
            star_rating=int(form.star_rating.data),
            review_text=form.review_text.data,
            attendee_type=form.attendee_type.data,
            would_recommend=form.would_recommend.data,
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        )
        review.set_categories(categories)

        db.session.add(review)
        db.session.commit()

        flash('Thank you for your review!', 'success')
        return redirect(url_for('main.review_success', unique_code=unique_code))

    return render_template('review/review_form.html', title=f'Review: {event.title}',
                         event=event, form=form)

@bp.route('/review/<string:unique_code>/success')
def review_success(unique_code):
    event = Event.query.filter_by(unique_code=unique_code).first_or_404()

    # Get some sample reviews to show
    recent_reviews = Review.query.filter_by(event_id=event.id, is_approved=True)\
                          .order_by(Review.submitted_at.desc()).limit(3).all()

    return render_template('review/review_success.html', title='Thank You!',
                         event=event, recent_reviews=recent_reviews)

@bp.route('/review/<string:unique_code>/browse')
def browse_reviews(unique_code):
    event = Event.query.filter_by(unique_code=unique_code).first_or_404()

    # Get all approved reviews
    reviews = Review.query.filter_by(event_id=event.id, is_approved=True)\
                    .order_by(Review.submitted_at.desc()).all()

    avg_rating = event.get_average_rating()
    rating_distribution = event.get_rating_distribution()

    return render_template('review/browse_reviews.html', title=f'Reviews: {event.title}',
                         event=event, reviews=reviews, avg_rating=avg_rating,
                         rating_distribution=rating_distribution)
