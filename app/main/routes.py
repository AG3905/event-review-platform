from flask import render_template, redirect, url_for, flash, request, jsonify, send_file, abort
from flask_login import login_required, current_user
from app.main import bp
from app.models import User, Event, Review, db
from app.forms import EventForm, ReviewForm, EditEventForm
from app.utils import generate_qr_code, export_reviews_csv
from datetime import datetime, date
from sqlalchemy import func
import os
from app.decorators import admin_required, organizer_required


def _owned_event_or_404(event_id):
    """Return an event only when it belongs to the logged-in organizer."""
    return Event.query.filter_by(id=event_id, user_id=current_user.id).first_or_404()

@bp.route('/')
def index():
    return render_template('index.html', title='Event Review Platform')


@bp.route('/health')
def health():
    # Simple health check endpoint for load balancers/hosts
    return jsonify({'status': 'ok'}), 200

@bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_platform_admin:
        return redirect(url_for('main.admin_dashboard'))

    events = Event.query.filter_by(user_id=current_user.id).order_by(Event.created_at.desc()).all()

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
@organizer_required
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
@organizer_required
def event_details(event_id):
    event = _owned_event_or_404(event_id)

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
@organizer_required
def edit_event(event_id):
    event = _owned_event_or_404(event_id)

    form = EditEventForm(obj=event)
    if form.validate_on_submit():
        form.populate_obj(event)
        event.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Event updated successfully!', 'success')
        return redirect(url_for('main.event_details', event_id=event.id))

    return render_template('dashboard/edit_event.html', title='Edit Event', form=form, event=event)


@bp.route('/event/<int:event_id>/delete', methods=['POST'])
@organizer_required
def delete_event(event_id):
    event = _owned_event_or_404(event_id)
    title = event.title
    db.session.delete(event)
    db.session.commit()
    flash(f'Event "{title}" and its reviews were deleted.', 'success')
    return redirect(url_for('main.dashboard'))

@bp.route('/event/<int:event_id>/qr')
@organizer_required
def event_qr_code(event_id):
    event = _owned_event_or_404(event_id)

    # Generate QR code
    review_url = request.url_root.rstrip('/') + event.get_review_url()
    qr_path = generate_qr_code(review_url, event.unique_code)

    return send_file(qr_path, as_attachment=True, download_name=f'{event.title}_QR.png')

@bp.route('/event/<int:event_id>/export')
@organizer_required
def export_event_reviews(event_id):
    event = _owned_event_or_404(event_id)

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


@bp.route('/admin')
@admin_required
def admin_dashboard():
    organizers = User.query.filter_by(role='organizer').order_by(User.created_at.desc()).all()
    events = Event.query.order_by(Event.created_at.desc()).all()
    recent_reviews = Review.query.order_by(Review.submitted_at.desc()).limit(10).all()
    return render_template(
        'admin/dashboard.html', title='Platform Admin Console', organizers=organizers,
        events=events, total_reviews=Review.query.count(), recent_reviews=recent_reviews
    )


@bp.route('/admin/organizers')
@admin_required
def admin_organizers():
    organizers = User.query.filter_by(role='organizer').order_by(User.created_at.desc()).all()
    return render_template('admin/organizers.html', title='Organizers', organizers=organizers)


@bp.route('/admin/events')
@admin_required
def admin_events():
    events = Event.query.order_by(Event.created_at.desc()).all()
    return render_template('admin/events.html', title='All Events', events=events)


@bp.route('/admin/reviews')
@admin_required
def admin_reviews():
    reviews = Review.query.order_by(Review.submitted_at.desc()).all()
    return render_template('admin/reviews.html', title='All Reviews', reviews=reviews)


@bp.route('/admin/analytics')
@admin_required
def admin_analytics():
    approved_reviews = Review.query.filter_by(is_approved=True).all()
    ratings = [review.star_rating for review in approved_reviews]
    return render_template(
        'admin/analytics.html', title='Platform Analytics',
        total_reviews=len(approved_reviews),
        average_rating=(sum(ratings) / len(ratings)) if ratings else 0,
        total_organizers=User.query.filter_by(role='organizer').count(),
        total_events=Event.query.count(),
    )


@bp.route('/reviews')
@organizer_required
def organizer_reviews():
    reviews = Review.query.join(Event).filter(Event.user_id == current_user.id)\
        .order_by(Review.submitted_at.desc()).all()
    return render_template('dashboard/reviews.html', title='My Reviews', reviews=reviews)


@bp.route('/analytics')
@organizer_required
def organizer_analytics():
    events = Event.query.filter_by(user_id=current_user.id).all()
    reviews = Review.query.join(Event).filter(Event.user_id == current_user.id,
                                               Review.is_approved.is_(True)).all()
    ratings = [review.star_rating for review in reviews]
    return render_template(
        'dashboard/analytics.html', title='My Analytics', events=events,
        total_reviews=len(reviews),
        average_rating=(sum(ratings) / len(ratings)) if ratings else 0,
    )
