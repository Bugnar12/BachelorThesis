import email
import joblib
from email import policy
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

def load_model():
    """Loads the AI model that predicts phishing based on email body and returns it."""
    model = joblib.load(AI_MODEL_ABS_PATH)
    return model