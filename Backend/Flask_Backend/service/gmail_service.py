import json

from database import db
from model.email import Email
from repository.repository import Repository
from service.email_service import EmailService
from service.push_notification_service import PushNotificationService
from service.virustotal_service import VirusTotalService
from utils import email_utils
from utils.email_utils import get_credentials_for_user, unshorten_url, is_url_shortened, save_attachment_temp
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
            user_id=user_id,
            gmail_message_id=message_id,
            email_sender=sender,
            email_subject=subject,
            email_recipient=recipient,
            email_body=decoded_body
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
        text_result = self.__email_service.predict_email_text(email.email_id)
        text_pred_label = text_result.get("prediction", "").lower()
        email.text_prediction = json.dumps(text_result)

        url = email_utils.extract_url_from_body(email.email_body)
        vt_label = "No URL"
        url_label = "No URL"

        if url:
            final_url = unshorten_url(url) if is_url_shortened(url) else url

            url_result = self.__email_service.predict_url(final_url)
            url_label = url_result.get("label", "unknown").lower()
            email.url_prediction = json.dumps(url_result)

            vt_result = self.__email_service.predict_url_virustotal(final_url)
            vt_pred_raw = vt_result.get("prediction", [])
            vt_label = vt_pred_raw[0].lower() if isinstance(vt_pred_raw, list) and vt_pred_raw else "unknown"
            email.vt_domain_prediction = vt_label
        else:
            logger.warning("No URL found in email body")

        verdict = "legitimate"
        if "phishing" in text_pred_label or "phishing" in url_label or "phishing" in vt_label:
            verdict = "phishing"

        email.final_verdict = verdict

        logger.info("[Verdict] Final verdict for email with ID {}: {}".format(email.email_id, verdict))

        # notify user
        user = self.__repository.get_user_by_id(email.user_id)
        self.__push_service.notify_user_phishing_email(user, email.email_subject, email.email_sender)

        self.__repository.commit()

    def process_notification(self, email_address, history_id):
        user = self.__get_user_and_check_creds(email_address)
        if not user:
            return

        service = self.__build_gmail_service(email_address)
        messages = self.__fetch_new_messages(service, user, history_id)
        if not messages:
            return

        self.__process_messages(messages, service, user, email_address, history_id)

    def get_user_by_email(self, email_address):
        user = self.__repository.get_user_by_email(email_address)
        if not user:
            logger.warning("No user found for email: {}".format(email_address))
            return None
        return user

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
                self.classify_email(email)
            user.last_history_id = history_id
            db.session.commit()
        except Exception as e:
            logger.exception("Error processing messages: {}".format(e))
            db.session.rollback()