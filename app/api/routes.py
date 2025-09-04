from flask import jsonify, request
from flask_login import login_required, current_user
from app.api import bp
from app.models import Event, Review, db

@bp.route('/review/<int:review_id>/approve', methods=['POST'])
@login_required
def approve_review(review_id):
    review = Review.query.get_or_404(review_id)

    # Check ownership
    if review.event.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    review.is_approved = True
    db.session.commit()

    return jsonify({'success': True, 'message': 'Review approved'})

@bp.route('/review/<int:review_id>/reject', methods=['POST'])
@login_required
def reject_review(review_id):
    review = Review.query.get_or_404(review_id)

    # Check ownership
    if review.event.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    review.is_approved = False
    db.session.commit()

    return jsonify({'success': True, 'message': 'Review rejected'})

@bp.route('/review/<int:review_id>/feature', methods=['POST'])
@login_required
def feature_review(review_id):
    review = Review.query.get_or_404(review_id)

    # Check ownership
    if review.event.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

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
    review = Review.query.get_or_404(review_id)

    # Check ownership
    if review.event.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    db.session.delete(review)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Review deleted'})

@bp.route('/event/<int:event_id>/analytics', methods=['GET'])
@login_required
def event_analytics(event_id):
    event = Event.query.get_or_404(event_id)

    # Check ownership
    if event.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

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
