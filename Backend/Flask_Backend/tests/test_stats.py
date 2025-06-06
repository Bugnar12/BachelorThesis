def test_get_email_stats(client, mocker, auth_header):
    # Mock response returned by stats_service.get_summary_for_user
    mock_result = {
        'total': 10,
        'phishing': 4,
        'legitimate': 6,
        'detection_breakdown': {
            'ai_url': 2,
            'ai_text': 1,
            'vt': 1,
            'uncategorized': 6
        },
        'timeline': [
            {'date': '2024-06-01', 'count': 2},
            {'date': '2024-06-02', 'count': 1}
        ]
    }

    mocker.patch(
        'routes.email_routes.stats_service.get_summary_for_user',
        return_value=(mock_result, 200)
    )

    response = client.get('/emails/stats', headers=auth_header)
    assert response.status_code == 200
    data = response.get_json()

    assert 'total' in data
    assert 'phishing' in data
    assert 'legitimate' in data
    assert 'detection_breakdown' in data
    assert 'timeline' in data

    assert data['phishing'] == 4
    assert data['detection_breakdown']['ai_url'] == 2
