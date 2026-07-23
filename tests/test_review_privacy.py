from app.models import Review, db


def test_public_pages_do_not_leak_private_data(client, sample_event):
    rev = Review(
        event_id=sample_event.id,
        reviewer_name='Secret Reviewer',
        reviewer_email='private_email@example.com',
        reviewer_town='Secret Town',
        reviewer_state='Secret State',
        star_rating=5,
        review_text='Great event!',
        is_approved=True
    )
    db.session.add(rev)
    db.session.commit()

    # 1. Check browse_reviews page HTML
    res_browse = client.get(f'/review/{sample_event.unique_code}/browse')
    assert res_browse.status_code == 200
    html_browse = res_browse.data.decode('utf-8')
    assert 'Secret Reviewer' in html_browse
    assert 'Secret Town' not in html_browse
    assert 'Secret State' not in html_browse
    assert 'private_email@example.com' not in html_browse

    # 2. Check review_success page HTML
    res_success = client.get(f'/review/{sample_event.unique_code}/success')
    assert res_success.status_code == 200
    html_success = res_success.data.decode('utf-8')
    assert 'Secret Town' not in html_success
    assert 'Secret State' not in html_success
    assert 'private_email@example.com' not in html_success
