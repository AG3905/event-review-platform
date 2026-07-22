def test_login_rate_limit(client):
    # Route limit is 5 per minute
    statuses = []
    for i in range(6):
        response = client.post('/auth/login', data={
            'username': 'nonexistent',
            'password': 'Password123!'
        })
        statuses.append(response.status_code)

    assert 429 in statuses

def test_submit_review_rate_limit(client, sample_event):
    # Route limit is 10 per hour
    statuses = []
    for i in range(12):
        response = client.post(f'/review/{sample_event.unique_code}/submit', data={
            'reviewer_name': f'Spammer {i}',
            'reviewer_email': f'spammer{i}@example.com',
            'star_rating': 3
        })
        statuses.append(response.status_code)

    assert 429 in statuses
