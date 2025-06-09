import json
from datetime import timedelta

from flask import Blueprint, redirect, session, request, jsonify
from flask_jwt_extended import create_access_token
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

from config.config import GmailConfig
from database import db
from model.user import User
from service.gmail_service import GmailService
from utils import email_utils
from utils.definitions import FRONTEND_BASE_URL
from utils.logs import get_logger

gmail_bp = Blueprint("gmail", __name__, url_prefix="/gmail")

gmail_service = GmailService(db.session)
logger = get_logger()

@gmail_bp.route("/authorize", methods=["GET"])
def authorize():
    # session.clear() was here before
    logger.info("Session before setting state: {}".format(dict(session)))
    auth_flow = Flow.from_client_secrets_file(
        GmailConfig.get_secret_file_path(),
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
    logger.info("State in session: {session.get('state')}")
    state = session.get('state')
    if not state or state != returned_state:
        return "Missing or mismatching state", 400

    callback_flow = Flow.from_client_secrets_file(
        GmailConfig.get_secret_file_path(),
        GmailConfig.GMAIL_SCOPE,
        state=state,
        redirect_uri=GmailConfig.REDIRECT_URI
    )
    callback_flow.fetch_token(authorization_response=request.url)
    creds = callback_flow.credentials

    service = build('gmail', 'v1', credentials=creds)
    profile = service.users().getProfile(userId='me').execute()
    email = profile['emailAddress']
    user = gmail_service.get_user_by_email(email)

    # Service for watching the inbox gmail of the user using Gmail API
    watch_request_body = {
        "labelIds": ["INBOX"],
        "topicName": GmailConfig.GMAIL_SUBSCRIPTION_TOPIC
    }
    watch_response = service.users().watch(userId='me', body=watch_request_body).execute()
    new_history_id = watch_response.get("historyId")
    logger.info("Watch started for user with email {}: {}".format(email, watch_response))

    if not user:
        user = User(user_email=email, last_history_id=new_history_id)
        db.session.add(user)
        db.session.commit()

    user.last_history_id = new_history_id
    db.session.commit()

    gmail_service.handle_oauth_callback(creds, user)
    # JWT authorization
    access_token = create_access_token(identity=str(user.user_id), expires_delta=timedelta(minutes=15))
    logger.info("Access token log: {}".format(access_token))
    # modify this after testing -> increase the expiration time by a lot
    refresh_token = create_access_token(identity=str(user.user_id), expires_delta=timedelta(minutes=31))

    return redirect("{}/dashboard?access_token={}&refresh_token={}".format(
        FRONTEND_BASE_URL, access_token, refresh_token)
    )


@gmail_bp.route("/notification", methods=["POST"])
def fetch_gmail_notif():
    try:
        envelope = request.get_json()
        message = envelope.get("message")
        decoded_data = email_utils.decode_data(message['data'])
        parsed_data = json.loads(decoded_data)

        email_address = parsed_data['emailAddress']
        history_id = parsed_data['historyId']

        gmail_service.process_notification(email_address, history_id)
        logger.info("Gmail data received: {}".format(parsed_data))

        return "Status 200", 200
    except Exception as e:
        logger.exception("Error occurred in fetching gmail notifications: {}".format(e))
        return jsonify({"error": "Failed to fetch gmail notifications"}), 500
