from database import db
from model.email import Email
from repository.repository import Repository
from service.email_service import EmailService
from service.push_notification_service import PushNotificationService
from utils import email_utils
from utils.email_utils import get_credentials_for_user, unshorten_url, is_url_shortened
from utils.logs import get_logger
from googleapiclient.discovery import build

logger = get_logger()


class GmailService:
    def __init__(self, db_session):
        self.__repository = Repository(db_session)
        self.__email_service = EmailService(db_session)
        self.__push_service = PushNotificationService(db_session)

    def handle_oauth_callback(self, creds, user):
        self.__repository.save_token(creds, user)

    def classify_email_text(self, email_id):
        return self.__email_service.predict_email_text(email_id)

    def classify_url(self, email_body):
        return self.__email_service.predict_url(email_body)

    def extract_fields_and_save_email(self, msg, email_address, user_id):
        message_id = msg.get("id")
        # Avoid duplicate emails (even though they should not really produces)
        preexisting_email = self.__repository.get_email_by_gmail_message_id(message_id)
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
        email_text_prediction = self.classify_email_text(email.email_id)
        logger.info("TEXT PREDICTION: {}".format(email_text_prediction))
        email_url = email_utils.extract_url_from_body(email.email_body)
        if email_url:
            # First check if the URL is shortened and unshorten it if necessary, then predict
            final_url = unshorten_url(email_url) if is_url_shortened(email_url) else email_url
            email_url_prediction = self.classify_url(final_url)
            logger.info("URL PREDICTION: {}".format(email_url_prediction))
            # user = User.query.get(email.user_id)
            user = self.__repository.get_user_by_id(email.user_id)
            self.__push_service.notify_user_phishing_email(user, email.email_subject, email.email_sender)
        else:
            logger.warning("No URL found in email with ID: {}".format(email.email_id))

    """
    Will process the push notification by extracting the whole email content from the history id
    """
    def process_notification(self, email_address, history_id):
        user = self.__repository.get_user_by_email(email_address)
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
