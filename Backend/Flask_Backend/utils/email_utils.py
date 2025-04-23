import base64
import email
import re
import joblib
from email import policy
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from database import db
from model.user import User
from utils.definitions import AI_MODEL_ABS_PATH


def parse_email(email_file_path):
    """Parses the raw .eml file and extracts its content in a more readable form."""
    with open(email_file_path, "r", encoding="utf-8") as f:
        email_content = email.message_from_file(f, policy=policy.default)
    return email_content

def get_email_header(email_content):
    """Extracts the header from the email content."""
    header = dict(email_content.items())
    return header

def get_email_body(email_content):
    """Extracts the plain text body from the email content."""
    body = None
    if email_content.is_multipart():
        for part in email_content.walk():
            if part.get_content_type() == "text/plain":  # Extract plain text body
                body = part.get_payload(decode=True).decode(part.get_content_charset(), errors="ignore")
                break  # Stop after getting the first plain text part
    else:
        body = email_content.get_payload(decode=True).decode(email_content.get_content_charset(), errors="ignore")

    return body

def extract_decode_email_body(email_payload):
    if 'parts' in email_payload:
        for part in email_payload['parts']:
            # MIME can be text/plain or text/html
            mime = part.get('mimeType')
            data = part.get('body', {}).get('data')
            if data:
                decoded_text = base64.urlsafe_b64decode(data.encode('utf-8')).decode('utf-8')
                if mime == 'text/plain':
                    return decoded_text
    elif 'body' in email_payload and 'data' in email_payload['body']:
        return base64.urlsafe_b64decode(email_payload['body']['data'].encode('utf-8')).decode('utf-8')

def load_model():
    """Loads the AI model that predicts phishing based on email body and returns it."""
    model = joblib.load(AI_MODEL_ABS_PATH)
    return model

def build_credentials_for_user(user):
    """
    Builds the Gmail API credentials for a given user based on the associated GmailToken.
    """
    gmail_token = user.gmail_token  # assuming one-to-one relationship via backref

    if not gmail_token:
        raise ValueError(f"No Gmail token found for user {user.user_email}")

    creds = Credentials(
        token=gmail_token.access_token,
        refresh_token=gmail_token.refresh_token,
        id_token=gmail_token.id_token,
        token_uri=gmail_token.token_uri,
        client_id=gmail_token.client_id,
        client_secret=gmail_token.client_secret,
        scopes=gmail_token.scopes.split(",") if isinstance(gmail_token.scopes, str) else gmail_token.scopes
    )

    return creds

def get_credentials_for_user(email_address):
    """
    Load and refresh Gmail API credentials for a user by email address.
    """
    user = User.query.filter_by(user_email=email_address).first()

    if not user or not user.gmail_token:
        return None

    token = user.gmail_token

    creds = Credentials(
        token=token.access_token,
        refresh_token=token.refresh_token,
        id_token=token.id_token,
        token_uri=token.token_uri,
        client_id=token.client_id,
        client_secret=token.client_secret,
        scopes=token.scopes.split(",") if isinstance(token.scopes, str) else token.scopes
    )

    # Refresh expired refresh_token
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

        token.access_token = creds.token
        db.session.commit()

    return creds

def extract_url_from_body(body):
    url_pattern = r"https?://[^\s]+"
    return re.findall(url_pattern, body)