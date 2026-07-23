def test_event_review_count_endpoint_scoping(client, organizer_user, sample_event, other_organizer_user, other_event):
    # Unauthenticated should fail / redirect or 401/403
    res_anon = client.get(f'/api/event/{sample_event.id}/review-count')
    assert res_anon.status_code in (302, 401)

    # Login as organizer 1
    client.post('/auth/login', data={'username': 'organizer1', 'password': 'Password123!'})

    # Organizer 1 can query own event
    res_own = client.get(f'/api/event/{sample_event.id}/review-count')
    assert res_own.status_code == 200
    data_own = res_own.get_json()
    assert 'total_reviews' in data_own
    assert 'average_rating' in data_own

    # Organizer 1 CANNOT query organizer 2's event
    res_other = client.get(f'/api/event/{other_event.id}/review-count')
    assert res_other.status_code == 404


def test_dashboard_summary_endpoint(client, organizer_user):
    client.post('/auth/login', data={'username': 'organizer1', 'password': 'Password123!'})
    res = client.get('/api/dashboard/summary')
    assert res.status_code == 200
    data = res.get_json()
    assert 'total_events' in data
    assert 'total_reviews' in data
    assert 'avg_rating' in data


def test_admin_summary_endpoint_security(client, organizer_user, admin_user):
    # Regular organizer hitting admin endpoint fails
    client.post('/auth/login', data={'username': 'organizer1', 'password': 'Password123!'})
    res_org = client.get('/api/admin/summary')
    assert res_org.status_code == 403

    # Logout organizer 1 first
    client.get('/auth/logout')

    # Admin hitting admin endpoint succeeds
    client.post('/auth/login', data={'username': 'admin1', 'password': 'Password123!'})
    res_admin = client.get('/api/admin/summary')
    assert res_admin.status_code == 200
    data = res_admin.get_json()
    assert 'total_organizers' in data
    assert 'total_events' in data
