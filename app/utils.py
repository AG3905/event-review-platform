import io
import qrcode
from PIL import Image
import os
import csv
from datetime import datetime

PER_PAGE = 25


def generate_qr_code(url, filename=None):
    """Generate QR code for event review URL in memory (BytesIO)"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)

    # Storage path can be optionally enabled in production via FILE_STORAGE_PATH
    storage_base = os.environ.get('FILE_STORAGE_PATH')
    if storage_base and filename:
        qr_dir = os.path.join(storage_base, 'qr_codes')
        os.makedirs(qr_dir, exist_ok=True)
        img.save(os.path.join(qr_dir, f'{filename}.png'))

    return buf


def export_reviews_csv(event):
    """Export event reviews to an in-memory BytesIO CSV buffer"""
    string_io = io.StringIO()

    active_questions = [q for q in event.questions if q.is_active]

    fieldnames = [
        'Review ID', 'Reviewer Name', 'Reviewer Email', 'Reviewer Town', 'Reviewer State',
        'Star Rating', 'Review Text', 'Categories', 'Attendee Type', 'Would Recommend',
        'Submitted At', 'Is Approved', 'Is Featured', 'Quality Score'
    ] + [q.question_text for q in active_questions]

    writer = csv.DictWriter(string_io, fieldnames=fieldnames)
    writer.writeheader()

    for review in event.reviews:
        answers_map = {ans.question_id: ans.answer_text for ans in review.answers}
        row = {
            'Review ID': review.id,
            'Reviewer Name': review.reviewer_name,
            'Reviewer Email': review.reviewer_email,
            'Reviewer Town': review.reviewer_town or '',
            'Reviewer State': review.reviewer_state or '',
            'Star Rating': review.star_rating,
            'Review Text': review.review_text or '',
            'Categories': ', '.join(review.get_categories()),
            'Attendee Type': review.attendee_type or '',
            'Would Recommend': 'Yes' if review.would_recommend else 'No',
            'Submitted At': review.submitted_at.strftime('%Y-%m-%d %H:%M:%S'),
            'Is Approved': 'Yes' if review.is_approved else 'No',
            'Is Featured': 'Yes' if review.is_featured else 'No',
            'Quality Score': review.get_quality_score()
        }
        for q in active_questions:
            row[q.question_text] = answers_map.get(q.id, '')
        writer.writerow(row)

    csv_bytes = string_io.getvalue().encode('utf-8')
    buf = io.BytesIO(csv_bytes)

    # Storage path can be optionally enabled in production via FILE_STORAGE_PATH
    storage_base = os.environ.get('FILE_STORAGE_PATH')
    if storage_base:
        csv_dir = os.path.join(storage_base, 'exports')
        os.makedirs(csv_dir, exist_ok=True)
        filename = f'reviews_{event.unique_code}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        with open(os.path.join(csv_dir, filename), 'wb') as f:
            f.write(csv_bytes)

    return buf



def calculate_word_frequency(reviews):
    """Calculate word frequency from review texts"""
    word_freq = {}
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}

    for review in reviews:
        if review.review_text:
            words = review.review_text.lower().split()
            for word in words:
                # Clean word
                word = ''.join(c for c in word if c.isalnum())
                if len(word) > 2 and word not in stop_words:
                    word_freq[word] = word_freq.get(word, 0) + 1

    # Return top 20 words
    return dict(sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:20])

def format_datetime(dt):
    """Format datetime for display"""
    if not dt:
        return ''

    now = datetime.utcnow()
    diff = now - dt

    if diff.days > 0:
        return f'{diff.days} day{"s" if diff.days > 1 else ""} ago'
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f'{hours} hour{"s" if hours > 1 else ""} ago'
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f'{minutes} minute{"s" if minutes > 1 else ""} ago'
    else:
        return 'Just now'

def get_rating_color(rating):
    """Get color for rating display"""
    if rating >= 4.5:
        return '#16a34a'  # Green
    elif rating >= 3.5:
        return '#ca8a04'  # Yellow
    elif rating >= 2.5:
        return '#ea580c'  # Orange
    else:
        return '#dc2626'  # Red

def validate_password_strength(password):
    """Validate password strength"""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"

    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)

    score = sum([has_upper, has_lower, has_digit])

    if score < 2:
        return False, "Password should contain uppercase, lowercase, and numbers"

    return True, "Password is strong"
