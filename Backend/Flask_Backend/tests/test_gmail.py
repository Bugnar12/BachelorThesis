import pytest
from unittest.mock import MagicMock
from service.gmail_service import GmailService
from model.email import Email

@pytest.fixture
def mock_repo(mocker):
    mock_repo = MagicMock()
    mocker.patch('service.gmail_service.Repository', return_value=mock_repo)
    return mock_repo

@pytest.fixture
def gmail_service(mock_repo):
    return GmailService(db_session=MagicMock())

def test_classify_email_sets_verdict_phishing(gmail_service, mocker):
    email = Email.from_body_only(email_body='This is a phishing email with a link http://phish.com')

    # Patch internal service calls
    mocker.patch.object(gmail_service._GmailService__email_service, 'predict_email_text',
                        return_value={'prediction': 'phishing text'})
    mocker.patch.object(gmail_service._GmailService__email_service, 'predict_url',
                        return_value={'label': 'phishing'})
    mocker.patch.object(gmail_service._GmailService__email_service, 'predict_url_virustotal',
                        return_value={'prediction': ['phishing']})
    mocker.patch('utils.email_utils.extract_url_from_body', return_value=['http://phish.com'])
    mocker.patch('utils.email_utils.is_url_shortened', return_value=False)
    mocker.patch.object(gmail_service._GmailService__repository, 'get_user_by_id', return_value=MagicMock())
    mocker.patch.object(gmail_service._GmailService__push_service, 'notify_user_phishing_email')
    mocker.patch.object(gmail_service._GmailService__repository, 'commit')

    gmail_service.classify_email(email)

    assert email.final_verdict == 'phishing'


def test_extract_fields_and_save_email(gmail_service, mocker):
    fake_msg = {
        "id": "abc123",
        "payload": {
            "headers": [
                {"name": "Subject", "value": "Hello"},
                {"name": "From", "value": "someone@example.com"},
                {"name": "To", "value": "user@example.com"},
            ]
        }
    }
    mocker.patch.object(gmail_service._GmailService__repository, 'get_email_by_gmail_message_id', return_value=None)
    mocker.patch('utils.email_utils.extract_decode_email_body', return_value='Hello world')
    mocker.patch.object(gmail_service._GmailService__repository, 'save_email')

    email = gmail_service.extract_fields_and_save_email(fake_msg, "user@example.com", 1)

    assert email.email_subject == "Hello"
    assert email.email_sender == "someone@example.com"
    assert email.email_recipient == "user@example.com"
    assert email.email_body == "Hello world"
