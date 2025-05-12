import json

from database import db
from model.email import Email
from repository.repository import Repository
from service.email_service import EmailService
from service.push_notification_service import PushNotificationService
from service.virustotal_service import VirusTotalService
from utils import email_utils
from utils.email_utils import get_credentials_for_user, unshorten_url, is_url_shortened, compute_sha256, \
    save_attachment_temp
from utils.logs import get_logger
from googleapiclient.discovery import build

logger = get_logger()

vt_service = VirusTotalService()


class GmailService:
    def __init__(self, db_session):
        self.__repository = Repository(db_session)
        self.__email_service = EmailService(db_session)
        self.__push_service = PushNotificationService(db_session)

    def handle_oauth_callback(self, creds, user):
        self.__repository.save_token(creds, user)

    def extract_fields_and_save_email(self, msg, email_address, user_id):
        message_id = msg.get("id")
        # Avoid duplicate emails (even though they should not really produce)
        preexisting_email = self.__repository.get_email_by_gmail_message_id(message_id)
        if preexisting_email:
            return preexisting_email

        payload = msg['payload']
        headers = {h['name']: h['value'] for h in payload.get('headers', [])}

        subject = headers.get("Subject", "(No Subject)")
        sender = headers.get("From", "(Unknown Sender)")
        recipient = headers.get("To", email_address)
        decoded_body = email_utils.extract_decode_email_body(payload) or "No content"

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

    def extract_and_hash_attachments(self, service, msg):
        payload = msg['payload']
        parts = payload.get('parts', [])

        hashes = []

        for part in parts:
            if part.get('filename') and part['body'].get('attachmentId'):
                attachment_id = part['body']['attachmentId']
                attachment = service.users().messages().attachments().get(
                    userId='me',
                    id=attachment_id,
                    messageId=msg['id']
                ).execute()
                base64_data = attachment['data']
                hashes.append(base64_data)

        return hashes


    def classify_email(self, email):
        email_text_prediction = self.__email_service.predict_email_text(email.email_id)
        logger.info("TEXT PREDICTION: {}".format(email_text_prediction))
        email_url = email_utils.extract_url_from_body(email.email_body)
        if email_url:
            # First check if the URL is shortened and unshorten it if necessary, then predict
            final_url = unshorten_url(email_url) if is_url_shortened(email_url) else email_url
            email.url_prediction = self.__email_service.predict_url(final_url)
            # TODO: make this a utils function later (the serialization)
            email.url_prediction = json.dumps(email.url_prediction)
            logger.info("URL PREDICTION: {}".format(email.url_prediction))
            logger.info("vt: {}".format(self.__email_service.predict_url_virustotal(final_url)))
        else:
            logger.warning("No URL found in email body")
        user = self.__repository.get_user_by_id(email.user_id)
        self.__push_service.notify_user_phishing_email(user, email.email_subject, email.email_sender)

    """
    Will process the push notification by extracting the whole email content from the history id
    """

    def process_notification(self, email_address, history_id):
        user = self.__get_user_and_check_creds(email_address)
        if not user:
            return

        service = self.__build_gmail_service(email_address)
        messages = self.__fetch_new_messages(service, user, history_id)
        if not messages:
            return

        self.__process_messages(messages, service, user, email_address, history_id)

    def __get_user_and_check_creds(self, email_address):
        user = self.__repository.get_user_by_email(email_address)
        if not user or not user.gmail_token:
            logger.warning("No user or credentials for {}".format(email_address))
            return None
        return user

    def __build_gmail_service(self, email_address):
        creds = get_credentials_for_user(email_address)
        return build('gmail', 'v1', credentials=creds)

    def __fetch_new_messages(self, service, user, history_id):
        try:
            history = service.users().history().list(
                userId='me',
                startHistoryId=user.last_history_id,
                maxResults=10,
                historyTypes=['messageAdded']
            ).execute()

            messages = []
            for record in history.get('history', []):
                for msg in record.get('messagesAdded', []):
                    full_msg = service.users().messages().get(
                        userId='me',
                        id=msg['message']['id'],
                        format='full'
                    ).execute()
                    messages.append(full_msg)

            if messages:
                logger.info("{} new messages fetched.".format(len(messages)))
            else:
                logger.info("No new messages found for user: {}".format(user.user_email))

            return messages
        except Exception as e:
            logger.exception("Failed to fetch Gmail history.: {}".format(e))
            return []


    def __process_messages(self, messages, service, user, email_address, history_id):
        try:
            for msg in messages:
                email = self.extract_fields_and_save_email(msg, email_address, user.user_id)
                # attachment_hashes = self.extract_and_hash_attachments(service, msg)
                #
                # if attachment_hashes:
                #     data = email_utils.decode_data_padding(attachment_hashes[0])
                #     save_attachment_temp(data, "temp_file.txt")
                #     analysis_id = vt_service.check_file_hash("temp_file.txt")['data']['id']
                #     logger.info(vt_service.get_analysis_report(analysis_id))

                self.classify_email(email)
        except Exception as e:
            logger.exception("Error processing messages: {}".format(e))
            history_id = user.last_history_id
        finally:
            user.last_history_id = history_id
            db.session.commit()