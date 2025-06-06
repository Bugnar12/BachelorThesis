import json
from flask_jwt_extended import get_jwt_identity


def test_get_email_stats(client, auth_header, mocker):
    # Integration-style: hits endpoint, but with mocked service response
    mocker.patch(
        'routes.email_routes.EmailStatsService.get_summary_for_user',
        return_value={'total': 12, 'phishing': 3}
    )

    response = client.get('/emails/stats', headers=auth_header)
    assert response.status_code == 200
    data = response.get_json()
    assert data['total'] == 12
    assert data['phishing'] == 3


def test_analyze_email_url(client, auth_header, mocker):
    mock_data = {
        "url": "http://phish.test"
    }

    mocker.patch(
        'routes.email_routes.email_service.predict_url',
        return_value={"prediction": "phishing"}
    )

    response = client.post('/emails/predict_url', data=json.dumps(mock_data),
                           headers={**auth_header, "Content-Type": "application/json"})

    assert response.status_code == 200
    data = response.get_json()
    assert data['prediction'] == 'phishing'



def test_analyze_email_text(client, auth_header, mocker):
    mock_data = {
        "text": "You have won $1,000,000! Click here to claim your prize!"
    }

    mocker.patch(
        'routes.email_routes.email_service.predict_email_text',
        return_value={"prediction": "phishing"}
    )

    response = client.post(
        '/emails/predict_text',
        data=json.dumps(mock_data),
        headers={**auth_header, "Content-Type": "application/json"}
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data['prediction']['prediction'].lower() == 'phishing text'
