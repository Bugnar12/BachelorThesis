import base64
import email
import hashlib
import re
import string
import joblib
import requests
import spacy

from urllib.parse import urlparse, parse_qs, unquote
from email import policy
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

from bs4 import BeautifulSoup
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from unshortenit import UnshortenIt

from database import db
from model.user import User
from utils.definitions import AI_MODEL_ABS_PATH, URL_SHORTENERS, IMAGE_EXTENSIONS
from utils.logs import get_logger

logger = get_logger()


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
    stack = [email_payload]

    while stack:
        part = stack.pop()
        mime = part.get('mimeType')
        body = part.get('body', {})
        data = body.get('data')

        # Return decoded text if it's text/plain
        if mime == 'text/plain' and data:
            return base64.urlsafe_b64decode(data.encode('utf-8')).decode('utf-8')

        # If this part is multipart, add its subparts to the stack
        if 'parts' in part:
            stack.extend(part['parts'])

    # If no text/plain found, try top-level body
    if 'body' in email_payload and 'data' in email_payload['body']:
        data = email_payload['body']['data']
        if isinstance(data, list):
            data = data[0]
        return base64.urlsafe_b64decode(data.encode('utf-8')).decode('utf-8')

    return None


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
        # TODO: replace all f"" with .format()
        raise ValueError("No Gmail token found for user {}".format(user.user_email))

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

def extract_urls_from_body(body):
    logger.info("Raw HTML Body: {}".format(body))
    urls = set()

    plain_urls = re.findall(r'https?://[^\s\'"<>]+', body)
    urls.update(plain_urls)
    try:
        soup = BeautifulSoup(body, 'html.parser')
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if href.startswith('http'):
                urls.add(href)
    except Exception as e:
        logger.warning("Failed to parse HTML body: {}".format(e))

    return list(urls)

def postprocess_urls(urls: list) -> list:
    cleaned = set()

    for url in urls:
        url = unquote(url.strip())

        # Skip base64 images or image URLs
        if url.startswith("data:") or any(url.lower().endswith(ext) for ext in IMAGE_EXTENSIONS):
            continue

        # Google redirect wrapper
        if "google.com/url?q=" in url:
            parsed = urlparse(url)
            qs = parse_qs(parsed.query)
            real_url = qs.get("q", [None])[0]
            if real_url:
                url = unquote(real_url)

        # Googleusercontent proxy images
        if "googleusercontent.com" in url and "#http" in url:
            parts = url.split("#")
            if len(parts) > 1 and parts[1].startswith("http"):
                url = parts[1]

        # Skip known CDN image hosts
        if re.search(r"\.(png|jpg|jpeg|webp|gif|svg)(\?|$)", url, re.IGNORECASE):
            continue

        # Final check — only keep http(s) links
        if url.startswith("http"):
            cleaned.add(url)

    return list(cleaned)

def resolve_redirect_url(url: str, timeout: int = 3) -> str:
    try:
        resp = requests.head(url, allow_redirects=True, timeout=timeout)
        return resp.url  # Final destination
    except Exception as e:
        logger.warning("Redirect failed for {}: {}".format(url, e))
        return url  # Fallback: return original if resolution fails

def decode_data(data):
    try:
        if isinstance(data, list):
            # Take the first element or raise a meaningful error
            data = data[0]
        if not isinstance(data, str):
            raise ValueError("Expected string for base64 decode, got {}: {}".format(type(data), data))

        logger.info("Result data: {}".format(data))

        result_data = base64.b64decode(data.encode('utf-8')).decode('utf-8')
        return result_data
    except Exception as e:
        raise ValueError("Failed to decode base64 data: {}".format(e))

def decode_data_padding(data):
    if isinstance(data, list):
        data = data[0]
    if isinstance(data, str):
        data = data.encode()
    # Add padding if necessary
    missing_padding = len(data) % 4
    if missing_padding:
        data += b'=' * (4 - missing_padding)
    return base64.urlsafe_b64decode(data)

def is_url_shortened(url):
    if isinstance(url, list):
        if not url:
            return False
        url = url[0]
    domain = urlparse(url).netloc.lower()
    for short in URL_SHORTENERS:
        if short in domain:
            return True
    return False

def unshorten_url(url):
    unshorten_obj = UnshortenIt()
    try:
        return unshorten_obj.unshorten(url[0])
    except Exception as e:
        logger.warning("Unshortening failed: {}".format(e))
        return url[0]

def extract_domain(url):
    # TODO: process multiple URLs
    return urlparse(url[0]).netloc

def compute_sha256(base64_data):
    """Computes the SHA256 hash of a file."""
    binary_data = base64.urlsafe_b64decode(base64_data.encode('utf-8'))
    sha256_hash = hashlib.sha256(binary_data).hexdigest()

    return sha256_hash

def save_attachment_temp(decoded_bytes, filename):
    with open(filename, "wb") as f:
        f.write(decoded_bytes)


def preprocess_text(text):
    nlp = spacy.load("en_core_web_sm", disable=["ner", "parser"])
    nlp.max_length = 2_000_000_000
    stopwords_set = set(stopwords.words("english"))
    if not isinstance(text, str) or text.strip() == "":
        return ""

    text = text.lower()

    # Remove HTTP URLs
    text = re.sub(r'http\S+', '', text)
    # Remove digits
    text = re.sub(r'\d+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    # Remove special characters and punctuation
    text = text.translate(str.maketrans("", "", string.punctuation))

    # NLTK tokenization
    tokens = word_tokenize(text)
    tokens = [word for word in tokens if word not in stopwords_set]

    # Spacy lemmatization
    doc = nlp(" ".join(tokens))
    lemmatized_tokens = [token.lemma_ for token in doc]
    return " ".join(lemmatized_tokens)