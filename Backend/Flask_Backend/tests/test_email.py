# tests/test_email.py

def test_predict_text(client, mocker):
    mock_prediction = {'label': 'phishing', 'confidence': 0.92}
    mocker.patch(
        'routes.email_routes.email_service.predict_email_text_direct',
        return_value=mock_prediction
    )

    response = client.post('/emails/predict_text', json={
        'text': 'You have won a 50% discount on our product. Click here urgently to claim it!'
    })

    assert response.status_code == 200
    data = response.get_json()
    assert 'prediction' in data
    assert data['prediction']['label'] == 'phishing'


def test_predict_url(client, mocker):
    mock_result = {'label': 'phishing', 'confidence': 0.99}
    mocker.patch(
        'routes.email_routes.email_service.predict_url',
        return_value=mock_result
    )

    response = client.post('/emails/predict_url', json={'url': 'http://phish.site'})
    assert response.status_code == 200
    data = response.get_json()
    assert data['label'] == 'phishing'


def test_predict_email_from_extension(client, mocker):
    mock_result = {
        'text_prediction': 'phishing',
        'url_prediction': 'phishing',
        'vt_prediction': 'phishing',
        'verdict': 'phishing'
    }

    mocker.patch(
        'routes.email_routes.email_service.predict_from_extension',
        return_value=mock_result
    )

    response = client.post('/emails/predict/email', json={
        'subject': 'Suspicious',
        'sender': 'bad@evil.com',
        'body': 'Check out http://phish.site'
    })

    assert response.status_code == 200
    data = response.get_json()
    assert data['verdict'] == 'phishing'


def test_report_false_positive(client):
    response = client.post('/emails/report-fp', json={'id': 101, 'note': 'not phishing'})
    assert response.status_code == 200
    assert response.get_json() == {'status': 'ok'}


def test_get_emails(client, mocker, auth_header):
    mocker.patch(
        'routes.email_routes.email_service.get_paginated_emails_for_user',
        return_value={
            'items': [mocker.Mock(to_dict=lambda: {'id': 1, 'subject': 'Fake'})],
            'total': 1
        }
    )

    response = client.get('/emails/get_emails?page=1&page_size=10', headers=auth_header)
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['emails']) == 1
    assert data['emails'][0]['subject'] == 'Fake'


def test_get_email_stats(client, mocker, auth_header):
    mocker.patch(
        'routes.email_routes.EmailStatsService.get_summary_for_user',
        return_value={'total': 12, 'phishing': 3}
    )

    response = client.get('/emails/stats', headers=auth_header)
    assert response.status_code == 200
    data = response.get_json()
    assert data['total'] == 12
    assert data['phishing'] == 3

