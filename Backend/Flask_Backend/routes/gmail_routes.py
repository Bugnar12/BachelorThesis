from flask import Blueprint, redirect, session, request
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

from config.config import GmailConfig
from database import db
from model.user import User
from service.gmail_service import GmailService
from utils.logs import get_logger

gmail_bp = Blueprint("gmail", __name__, url_prefix="/gmail")

gmail_service = GmailService(db.session)
logger = get_logger()

@gmail_bp.route("/authorize", methods=["GET"])
def authorize():
    session.clear()  # Clear the session to avoid leftover data
    logger.info(f"Session before setting state: {dict(session)}")
    auth_flow = Flow.from_client_secrets_file(
        GmailConfig.CLIENT_SECRET_FILE,
        GmailConfig.GMAIL_SCOPE,
        redirect_uri=GmailConfig.REDIRECT_URI
    )

    auth_url, state = auth_flow.authorization_url(
        access_type="offline",
        prompt="consent",
        include_granted_scopes="true"
    )
    session['state'] = state
    logger.info(f"Session after setting state: {dict(session)}")
    return redirect(auth_url)

@gmail_bp.route("/oauth2callback", methods=["GET"])
def gmail_callback():
    returned_state = request.args.get('state')
    logger.info(f"State in session: {session.get('state')}")
    state = session.get('state')
    if not state or state != returned_state:
        return "Missing or mismatching state", 400

    callback_flow = Flow.from_client_secrets_file(
        GmailConfig.CLIENT_SECRET_FILE,
        GmailConfig.GMAIL_SCOPE,
        state=state,
        redirect_uri=GmailConfig.REDIRECT_URI
    )
    callback_flow.fetch_token(authorization_response=request.url)
    creds = callback_flow.credentials

    service = build('gmail', 'v1', credentials=creds)
    profile = service.users().getProfile(userId='me').execute()
    email = profile['emailAddress']

    user = User.query.filter_by(user_email=email).first()
    if not user:
        user = User(user_email=email)
        db.session.add(user)
        db.session.commit()

    gmail_service.handle_oauth_callback(creds, user)

    return f"Successfully authorized {email}"