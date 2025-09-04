import qrcode
from PIL import Image
import os
import csv
from io import StringIO
from datetime import datetime

def generate_qr_code(url, filename):
    """Generate QR code for event review URL"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    # Create QR code image
    img = qr.make_image(fill_color="black", back_color="white")

    # Save to static directory
    qr_dir = os.path.join('app', 'static', 'qr_codes')
    if not os.path.exists(qr_dir):
        os.makedirs(qr_dir)

    qr_path = os.path.join(qr_dir, f'{filename}.png')
    img.save(qr_path)

    return qr_path

def export_reviews_csv(event):
    """Export event reviews to CSV file"""
    csv_dir = os.path.join('app', 'static', 'exports')
    if not os.path.exists(csv_dir):
        os.makedirs(csv_dir)

    filename = f'reviews_{event.unique_code}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    csv_path = os.path.join(csv_dir, filename)

    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'Review ID', 'Reviewer Name', 'Reviewer Email', 'Star Rating',
            'Review Text', 'Categories', 'Attendee Type', 'Would Recommend',
            'Submitted At', 'Is Approved', 'Is Featured', 'Quality Score'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for review in event.reviews:
            writer.writerow({
                'Review ID': review.id,
                'Reviewer Name': review.reviewer_name,
                'Reviewer Email': review.reviewer_email,
                'Star Rating': review.star_rating,
                'Review Text': review.review_text or '',
                'Categories': ', '.join(review.get_categories()),
                'Attendee Type': review.attendee_type or '',
                'Would Recommend': 'Yes' if review.would_recommend else 'No',
                'Submitted At': review.submitted_at.strftime('%Y-%m-%d %H:%M:%S'),
                'Is Approved': 'Yes' if review.is_approved else 'No',
                'Is Featured': 'Yes' if review.is_featured else 'No',
                'Quality Score': review.get_quality_score()
            })

    return csv_path

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
