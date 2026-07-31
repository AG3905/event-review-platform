from flask import jsonify, request, abort
from flask_login import login_required, current_user
from app.api import bp
from app.models import Event, Review, SavedQuestionSet, User, db
from app.decorators import admin_required, organizer_required
from app.question_templates import suggest_questions_for, DEFAULT_LOCATION_QUESTIONS


def _manageable_review_or_404(review_id):
    if not (current_user.is_platform_admin or current_user.is_organizer):
        abort(403)
    query = Review.query.filter_by(id=review_id)
    if current_user.is_organizer:
        query = query.join(Event).filter(Event.user_id == current_user.id)
    return query.first_or_404()

@bp.route('/review/<int:review_id>/approve', methods=['POST'])
@login_required
def approve_review(review_id):
    review = _manageable_review_or_404(review_id)

    review.is_approved = True
    db.session.commit()

    return jsonify({'success': True, 'message': 'Review approved'})

@bp.route('/review/<int:review_id>/reject', methods=['POST'])
@login_required
def reject_review(review_id):
    review = _manageable_review_or_404(review_id)

    review.is_approved = False
    db.session.commit()

    return jsonify({'success': True, 'message': 'Review rejected'})

@bp.route('/review/<int:review_id>/feature', methods=['POST'])
@login_required
def feature_review(review_id):
    review = _manageable_review_or_404(review_id)

    review.is_featured = not review.is_featured
    db.session.commit()

    return jsonify({
        'success': True, 
        'message': 'Review featured' if review.is_featured else 'Review unfeatured',
        'is_featured': review.is_featured
    })

@bp.route('/review/<int:review_id>/delete', methods=['DELETE'])
@login_required
def delete_review(review_id):
    review = _manageable_review_or_404(review_id)

    db.session.delete(review)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Review deleted'})

@bp.route('/event/<int:event_id>/analytics', methods=['GET'])
@login_required
def event_analytics(event_id):
    if not (current_user.is_platform_admin or current_user.is_organizer):
        abort(403)
    query = Event.query.filter_by(id=event_id)
    if current_user.is_organizer:
        query = query.filter_by(user_id=current_user.id)
    event = query.first_or_404()

    reviews = [r for r in event.reviews if r.is_approved]

    # Calculate analytics
    analytics = {
        'total_reviews': len(reviews),
        'average_rating': event.get_average_rating(),
        'rating_distribution': event.get_rating_distribution(),
        'response_rate': event.get_response_rate(),
        'recent_activity': []
    }

    # Recent activity (last 7 days)
    from datetime import datetime, timedelta
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_reviews = [r for r in reviews if r.submitted_at >= week_ago]

    for review in recent_reviews:
        analytics['recent_activity'].append({
            'date': review.submitted_at.strftime('%Y-%m-%d'),
            'rating': review.star_rating,
            'reviewer': review.reviewer_name
        })

    return jsonify(analytics)

@bp.route('/check-email', methods=['POST'])
def check_email():
    data = request.get_json()
    email = data.get('email')
    unique_code = data.get('unique_code')

    if not email or not unique_code:
        return jsonify({'error': 'Missing data'}), 400

    event = Event.query.filter_by(unique_code=unique_code).first()
    if not event:
        return jsonify({'error': 'Event not found'}), 404

    existing_review = Review.query.filter_by(
        event_id=event.id,
        reviewer_email=email
    ).first()

    return jsonify({
        'exists': existing_review is not None,
        'message': 'You have already reviewed this event' if existing_review else 'Email available'
    })

@bp.route('/check-username', methods=['POST'])
def check_username():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    if not username:
        return jsonify({'available': False, 'message': 'Username is required'}), 400

    existing_user = User.query.filter_by(username=username).first()
    return jsonify({
        'available': existing_user is None,
        'message': 'Username is already taken' if existing_user else 'Username is available'
    })

@bp.route('/check-user-email', methods=['POST'])
def check_user_email():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    if not email:
        return jsonify({'available': False, 'message': 'Email is required'}), 400

    existing_user = User.query.filter_by(email=email).first()
    return jsonify({
        'available': existing_user is None,
        'message': 'Email is already registered' if existing_user else 'Email is available'
    })


@bp.route('/suggested-questions', methods=['GET'])
def get_suggested_questions():
    category = request.args.get('category', 'Other')
    suggested = suggest_questions_for(category)
    return jsonify({
        'suggested': suggested,
        'location': DEFAULT_LOCATION_QUESTIONS
    })

@bp.route('/saved-question-sets', methods=['GET'])
@organizer_required
def get_saved_question_sets():
    sets = SavedQuestionSet.query.filter_by(organizer_id=current_user.id).all()
    return jsonify([
        {
            'id': s.id,
            'name': s.name,
            'questions': s.get_questions()
        } for s in sets
    ])

@bp.route('/saved-question-sets', methods=['POST'])
@organizer_required
def save_question_set():
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    questions = data.get('questions', [])

    if not name:
        return jsonify({'error': 'Template name is required'}), 400
    if not questions:
        return jsonify({'error': 'Questions list cannot be empty'}), 400

    saved_set = SavedQuestionSet(organizer_id=current_user.id, name=name)
    saved_set.set_questions(questions)
    db.session.add(saved_set)
    db.session.commit()

    return jsonify({
        'success': True,
        'id': saved_set.id,
        'name': saved_set.name,
        'questions': saved_set.get_questions()
    })

@bp.route('/event/<int:event_id>/review-count', methods=['GET'])
@login_required
def event_review_count(event_id):
    if current_user.is_organizer:
        event = Event.query.filter_by(id=event_id, user_id=current_user.id).first_or_404()
    elif current_user.is_platform_admin:
        event = Event.query.filter_by(id=event_id).first_or_404()
    else:
        abort(403)

    reviews = event.reviews
    approved_reviews = [r for r in reviews if r.is_approved]
    pending_count = len([r for r in reviews if not r.is_approved])
    avg_rating = event.get_average_rating()
    
    last_review = max([r.submitted_at for r in reviews], default=None) if reviews else None
    last_review_at = last_review.isoformat() if last_review else None

    since_str = request.args.get('since')
    new_reviews_data = []
    if since_str:
        try:
            from datetime import datetime
            since_dt = datetime.fromisoformat(since_str)
            new_reviews = [r for r in reviews if r.submitted_at > since_dt]
            for r in new_reviews:
                new_reviews_data.append({
                    'id': r.id,
                    'reviewer_name': r.reviewer_name,
                    'star_rating': r.star_rating,
                    'review_text': r.review_text,
                    'is_approved': r.is_approved,
                    'is_featured': r.is_featured,
                    'submitted_at': r.submitted_at.isoformat()
                })
        except Exception:
            pass

    return jsonify({
        'total_reviews': len(reviews),
        'approved_count': len(approved_reviews),
        'pending_count': pending_count,
        'average_rating': avg_rating,
        'last_review_at': last_review_at,
        'new_reviews': new_reviews_data
    })

@bp.route('/dashboard/summary', methods=['GET'])
@organizer_required
def dashboard_summary():
    events = Event.query.filter_by(user_id=current_user.id).all()
    total_events = len(events)
    all_reviews = []
    for e in events:
        all_reviews.extend(e.reviews)
    
    total_reviews = len(all_reviews)
    approved_reviews = [r for r in all_reviews if r.is_approved]
    avg_rating = (sum(r.star_rating for r in approved_reviews) / len(approved_reviews)) if approved_reviews else 0
    last_review = max([r.submitted_at for r in all_reviews], default=None) if all_reviews else None
    
    return jsonify({
        'total_events': total_events,
        'total_reviews': total_reviews,
        'avg_rating': round(avg_rating, 2),
        'last_review_at': last_review.isoformat() if last_review else None
    })

@bp.route('/admin/summary', methods=['GET'])
@admin_required
def admin_summary():
    total_organizers = User.query.filter_by(role='organizer').count()
    total_events = Event.query.count()
    total_reviews = Review.query.count()
    approved_reviews = Review.query.filter_by(is_approved=True).all()
    avg_rating = (sum(r.star_rating for r in approved_reviews) / len(approved_reviews)) if approved_reviews else 0

    return jsonify({
        'total_organizers': total_organizers,
        'total_events': total_events,
        'total_reviews': total_reviews,
        'avg_rating': round(avg_rating, 2)
    })

