import requests

from service.classifier_service import ClassifierService
from database import db
from model.email import Email
from model.user import User
from repository.repository import Repository
from service.email_service import EmailService
from utils import email_utils
from utils.email_utils import get_credentials_for_user
from utils.logs import get_logger
from googleapiclient.discovery import build

logger = get_logger()


class GmailService:
    def __init__(self, db_session):
        self.__repository = Repository(db_session)
        self.__email_service = EmailService(db_session)

    def handle_oauth_callback(self, creds, user):
        self.__repository.save_token(creds, user)
#        poller = PollerService(current_app._get_current_object(), db.session)
#        poller.start_polling(user.user_id)

    def classify_email_text(self, email_id):
        return self.__email_service.predict_email_text(email_id)

    def classify_url(self, email_body):
        return self.__email_service.predict_url(email_body)

    def extract_fields_and_save_email(self, msg, email_address, user_id):
        message_id = msg.get("id")
        # Avoid duplicate emails (even though they should not really produces)
        preexisting_email = Email.query.filter_by(gmail_message_id=message_id).first()
        if preexisting_email:
            return preexisting_email

        payload = msg['payload']
        headers = {h['name']: h['value'] for h in payload.get('headers', [])}

        subject = headers.get("Subject", "(No Subject)")
        sender = headers.get("From", "(Unknown Sender)")
        recipient = headers.get("To", email_address)
        decoded_body = email_utils.extract_decode_email_body(payload)

        email_obj = Email(
            user_id = user_id,
            gmail_message_id = message_id,
            email_sender = sender,
            email_subject = subject,
            email_recipient = recipient,
            email_body = decoded_body
        )
        self.__repository.save_email(email_obj)

        return email_obj

    def classify_email(self, email):
        email_prediction = self.classify_email_text(email.email_id)
        email_url = email_utils.extract_url_from_body(email.email_body)
        if email_url:
            url_prediction = self.classify_url(email_utils.extract_url_from_body(email.email_body))
            logger.info("URL PREDICTION: {}".format(url_prediction))
        # TODO: small fix here -> log a message when an URL is not present
        logger.info("EMAIL PREDICTION: {}".format(email_prediction))

    """
    Will process the push notification by extracting the whole email content from the history id
    """
    def process_notification(self, email_address, history_id):
        user = User.query.filter_by(user_email=email_address).first()
        if not user or not user.gmail_token:
            logger.warning(f"No user or credentials for {email_address}")
            return

        creds = get_credentials_for_user(email_address)
        service = build('gmail', 'v1', credentials=creds)

        logger.info("Fetching since: {}".format(user.last_history_id))

        try:
            history = service.users().history().list(
                userId='me',
                startHistoryId=user.last_history_id,
                maxResults=10,
                historyTypes=['messageAdded']
            ).execute()

            found_messages = []

            for record in history.get('history', []):
                for msg in record.get('messagesAdded', []):
                    msg_id = msg['message']['id']
                    full_msg = service.users().messages().get(
                        userId='me',
                        id=msg_id,
                        format='full'
                    ).execute()
                    found_messages.append(full_msg)

            if not found_messages:
                logger.info("No new messages found in inbox for user: {}".format(user.user_email))

            logger.info("{} new messages fetched.".format(len(found_messages)))

            # for msg in found_messages:
            #     same logic as below

            email = self.extract_fields_and_save_email(found_messages[0], email_address, user.user_id)
            self.classify_email(email)

            # Update the last_history_id for correct fetching
            user.last_history_id = history.get("historyId", history_id)
            db.session.commit()

        except Exception as e:
            logger.exception("Failed to fetch Gmail history.")
