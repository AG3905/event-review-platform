from flask import render_template, redirect, url_for, flash, request, jsonify, send_file, abort
from flask_login import login_required, current_user
from app.main import bp
from app.models import User, Event, Review, EventQuestion, ReviewAnswer, SavedQuestionSet, db
from app import limiter

from app.forms import EventForm, ReviewForm, EditEventForm
from app.utils import generate_qr_code, export_reviews_csv, PER_PAGE

from datetime import datetime, date
from sqlalchemy import func
import os
import json
from app.decorators import admin_required, organizer_required


def _owned_event_or_404(event_id):
    """Return an event only when it belongs to the logged-in organizer."""
    return Event.query.filter_by(id=event_id, user_id=current_user.id).first_or_404()


def _sync_event_questions(event, questions_data):
    """
    Sync questions array (list of dicts) with event's EventQuestion records.
    Caps at 10 active questions. Soft-deactivates missing questions.
    """
    if not isinstance(questions_data, list):
        return

    # Cap active questions at 10
    questions_data = questions_data[:10]

    existing_questions = {q.id: q for q in event.questions}
    kept_q_ids = set()

    for idx, q_dict in enumerate(questions_data):
        q_id = q_dict.get('id')
        q_text = (q_dict.get('text') or q_dict.get('question_text') or '').strip()
        q_type = q_dict.get('type') or q_dict.get('question_type') or 'text'
        options_list = q_dict.get('options', [])
        if isinstance(options_list, str):
            try:
                options_list = json.loads(options_list)
            except Exception:
                options_list = [o.strip() for o in options_list.split(',') if o.strip()]
        is_req = bool(q_dict.get('required') or q_dict.get('is_required'))

        if not q_text:
            continue

        if q_id and int(q_id) in existing_questions:
            eq = existing_questions[int(q_id)]
            eq.question_text = q_text
            eq.question_type = q_type
            eq.set_options(options_list)
            eq.is_required = is_req
            eq.display_order = idx
            eq.is_active = True
            kept_q_ids.add(eq.id)
        else:
            eq = EventQuestion(
                event_id=event.id,
                question_text=q_text,
                question_type=q_type,
                is_required=is_req,
                display_order=idx,
                is_active=True
            )
            eq.set_options(options_list)
            db.session.add(eq)
            db.session.flush()
            kept_q_ids.add(eq.id)

    # Soft delete unkept questions
    for q_id, q_obj in existing_questions.items():
        if q_id not in kept_q_ids:
            q_obj.is_active = False

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
        if form.category.data == 'Other':
            cat_val = form.custom_category.data.strip()
            is_custom = True
        else:
            cat_val = form.category.data
            is_custom = False

        allow_loc = request.form.get('allow_location_questions', 'true').lower() in ('true', '1', 'on')

        event = Event(
            user_id=current_user.id,
            title=form.title.data,
            category=cat_val,
            is_custom_category=is_custom,
            description=form.description.data,
            venue=form.venue.data,
            event_date=form.event_date.data,
            event_time=form.event_time.data,
            capacity=form.capacity.data,
            allow_location_questions=allow_loc
        )
        db.session.add(event)
        db.session.commit()

        q_json_str = request.form.get('questions_json')
        if q_json_str:
            try:
                q_data = json.loads(q_json_str)
                _sync_event_questions(event, q_data)
                db.session.commit()
            except Exception:
                pass

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

    town_counts = {}
    state_counts = {}
    for r in approved_reviews:
        if r.reviewer_town:
            town = r.reviewer_town.strip().title()
            if town:
                town_counts[town] = town_counts.get(town, 0) + 1
        if r.reviewer_state:
            state = r.reviewer_state.strip().title()
            if state:
                state_counts[state] = state_counts.get(state, 0) + 1

    top_towns = sorted(town_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    top_states = sorted(state_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    active_questions = [q for q in event.questions if q.is_active]
    question_stats = []
    for q in active_questions:
        ans_list = [ans.answer_text for ans in q.answers if ans.review and ans.review.is_approved and ans.answer_text is not None]
        stat = {'question': q, 'total_answers': len(ans_list)}
        if q.question_type == 'rating':
            ratings = [int(a) for a in ans_list if a.isdigit()]
            stat['avg'] = round(sum(ratings) / len(ratings), 2) if ratings else 0
        elif q.question_type in ('single_choice', 'multi_choice'):
            dist = {}
            for a in ans_list:
                if q.question_type == 'multi_choice':
                    try:
                        vals = json.loads(a)
                    except Exception:
                        vals = [a]
                else:
                    vals = [a]
                for v in vals:
                    dist[v] = dist.get(v, 0) + 1
            stat['distribution'] = dist
        elif q.question_type == 'yes_no':
            yes_cnt = sum(1 for a in ans_list if a.lower() in ('yes', 'true', '1'))
            stat['yes_count'] = yes_cnt
            stat['no_count'] = len(ans_list) - yes_cnt
        question_stats.append(stat)

    return render_template('dashboard/event_details.html', title=f'Event: {event.title}',
                         event=event, reviews=approved_reviews, avg_rating=avg_rating,
                         rating_distribution=rating_distribution, response_rate=response_rate,
                         top_towns=top_towns, top_states=top_states, question_stats=question_stats)

@bp.route('/event/<int:event_id>/edit', methods=['GET', 'POST'])
@organizer_required
def edit_event(event_id):
    event = _owned_event_or_404(event_id)

    form = EditEventForm(obj=event)

    if request.method == 'GET':
        if event.is_custom_category:
            form.category.data = 'Other'
            form.custom_category.data = event.category
        else:
            form.category.data = event.category

    if form.validate_on_submit():
        if form.category.data == 'Other':
            event.category = form.custom_category.data.strip()
            event.is_custom_category = True
        else:
            event.category = form.category.data
            event.is_custom_category = False

        event.title = form.title.data
        event.description = form.description.data
        event.venue = form.venue.data
        event.event_date = form.event_date.data
        event.event_time = form.event_time.data
        event.capacity = form.capacity.data
        event.status = form.status.data
        event.allow_reviews = form.allow_reviews.data
        if 'allow_location_questions' in request.form:
            event.allow_location_questions = request.form.get('allow_location_questions', 'true').lower() in ('true', '1', 'on')
        event.updated_at = datetime.utcnow()

        q_json_str = request.form.get('questions_json')
        if q_json_str is not None:
            try:
                q_data = json.loads(q_json_str)
                _sync_event_questions(event, q_data)
            except Exception:
                pass

        db.session.commit()
        flash('Event updated successfully!', 'success')
        return redirect(url_for('main.event_details', event_id=event.id))

    active_questions = EventQuestion.query.filter_by(event_id=event.id, is_active=True).order_by(EventQuestion.display_order).all()
    return render_template('dashboard/edit_event.html', title='Edit Event', form=form, event=event, active_questions=active_questions)


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

    # Generate QR code in memory
    review_url = request.url_root.rstrip('/') + event.get_review_url()
    qr_buf = generate_qr_code(review_url, event.unique_code)

    return send_file(qr_buf, mimetype='image/png', as_attachment=True, download_name=f'{event.title}_QR.png')

@bp.route('/event/<int:event_id>/export')
@organizer_required
def export_event_reviews(event_id):
    event = _owned_event_or_404(event_id)

    # Export reviews to CSV in memory
    csv_buf = export_reviews_csv(event)
    return send_file(csv_buf, mimetype='text/csv', as_attachment=True, download_name=f'{event.title}_reviews.csv')


@bp.route('/review/<string:unique_code>')
def review_form(unique_code):
    event = Event.query.filter_by(unique_code=unique_code).first_or_404()

    if not event.allow_reviews:
        return render_template('review/reviews_disabled.html', event=event)

    form = ReviewForm()
    questions = EventQuestion.query.filter_by(event_id=event.id, is_active=True).order_by(EventQuestion.display_order).all()
    return render_template('review/review_form.html', title=f'Review: {event.title}',
                         event=event, form=form, questions=questions)

@bp.route('/review/<string:unique_code>/submit', methods=['POST'])
@limiter.limit("10 per hour")
def submit_review(unique_code):
    event = Event.query.filter_by(unique_code=unique_code).first_or_404()

    if not event.allow_reviews:
        flash('Reviews are not allowed for this event.', 'error')
        return redirect(url_for('main.review_form', unique_code=unique_code))

    form = ReviewForm()
    questions = EventQuestion.query.filter_by(event_id=event.id, is_active=True).order_by(EventQuestion.display_order).all()

    if form.validate_on_submit():
        # Honeypot bot mitigation check
        if form.website.data:
            return redirect(url_for('main.review_success', unique_code=unique_code))

        # Check if user already reviewed this event
        existing_review = Review.query.filter_by(
            event_id=event.id,
            reviewer_email=form.reviewer_email.data
        ).first()

        if existing_review:
            flash('You have already submitted a review for this event.', 'warning')
            return redirect(url_for('main.review_success', unique_code=unique_code))

        # Dynamic questions validation loop
        answers_to_save = []
        for q in questions:
            if q.question_type == 'multi_choice':
                raw_val = request.form.getlist(f'question_{q.id}')
                ans_str = json.dumps(raw_val) if raw_val else ''
                is_empty = len(raw_val) == 0
            else:
                raw_val = request.form.get(f'question_{q.id}', '').strip()
                ans_str = raw_val
                is_empty = not raw_val

            if q.is_required and is_empty:
                flash(f'Please answer the required question: "{q.question_text}"', 'error')
                return render_template('review/review_form.html', title=f'Review: {event.title}', event=event, form=form, questions=questions)

            if q.question_type == 'rating' and ans_str:
                try:
                    val = int(ans_str)
                    if val < 1 or val > 5:
                        flash(f'Rating for "{q.question_text}" must be between 1 and 5', 'error')
                        return render_template('review/review_form.html', title=f'Review: {event.title}', event=event, form=form, questions=questions)
                except ValueError:
                    flash(f'Invalid rating for "{q.question_text}"', 'error')
                    return render_template('review/review_form.html', title=f'Review: {event.title}', event=event, form=form, questions=questions)

            if q.question_type in ('single_choice', 'multi_choice') and ans_str:
                valid_opts = q.get_options()
                check_vals = json.loads(ans_str) if q.question_type == 'multi_choice' else [ans_str]
                for cv in check_vals:
                    if valid_opts and cv not in valid_opts:
                        flash(f'Invalid choice for "{q.question_text}"', 'error')
                        return render_template('review/review_form.html', title=f'Review: {event.title}', event=event, form=form, questions=questions)

            if not is_empty:
                answers_to_save.append((q.id, ans_str))

        # Create review categories list for legacy back-compat
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
            reviewer_town=form.reviewer_town.data.strip() if form.reviewer_town.data else None,
            reviewer_state=form.reviewer_state.data.strip() if form.reviewer_state.data else None,
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

        for q_id, ans_str in answers_to_save:
            ans_obj = ReviewAnswer(review_id=review.id, question_id=q_id, answer_text=ans_str)
            db.session.add(ans_obj)
        db.session.commit()

        flash('Thank you for your review!', 'success')
        return redirect(url_for('main.review_success', unique_code=unique_code))

    return render_template('review/review_form.html', title=f'Review: {event.title}',
                         event=event, form=form, questions=questions)

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

    page = request.args.get('page', 1, type=int)
    reviews = Review.query.filter_by(event_id=event.id, is_approved=True)\
                    .order_by(Review.submitted_at.desc())\
                    .paginate(page=page, per_page=PER_PAGE, error_out=False)

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
    page = request.args.get('page', 1, type=int)
    organizers = User.query.filter_by(role='organizer').order_by(User.created_at.desc())\
        .paginate(page=page, per_page=PER_PAGE, error_out=False)
    return render_template('admin/organizers.html', title='Organizers', organizers=organizers)


@bp.route('/admin/events')
@admin_required
def admin_events():
    page = request.args.get('page', 1, type=int)
    events = Event.query.order_by(Event.created_at.desc())\
        .paginate(page=page, per_page=PER_PAGE, error_out=False)
    return render_template('admin/events.html', title='All Events', events=events)


@bp.route('/admin/reviews')
@admin_required
def admin_reviews():
    page = request.args.get('page', 1, type=int)
    reviews = Review.query.order_by(Review.submitted_at.desc())\
        .paginate(page=page, per_page=PER_PAGE, error_out=False)
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
    page = request.args.get('page', 1, type=int)
    reviews = Review.query.join(Event).filter(Event.user_id == current_user.id)\
        .order_by(Review.submitted_at.desc())\
        .paginate(page=page, per_page=PER_PAGE, error_out=False)
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
