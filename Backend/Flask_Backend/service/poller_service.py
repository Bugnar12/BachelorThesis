import base64
import threading
import time
import requests
from googleapiclient.discovery import build

from model.email import Email
from repository.repository import Repository
from utils.definitions import POLLING_INTERVAL
from utils.email_utils import build_credentials_for_user
from utils.logs import get_logger


logger = get_logger()

class PollerService:
    def __init__(self, app, db_session):
        self.app = app
        self.__repository = Repository(db_session)

    def start_polling(self, user_id):
        logger.info("Starting gmail polling service...")
        polling_thread = threading.Thread(target=self.poll_emails, args=(user_id,), daemon=True)
        polling_thread.start()
        # TODO: join should not be needed because always when the main thread stops this does too (?)

    def fetch_email_content(self, user, message_id):
        creds = build_credentials_for_user(user)
        service = build("gmail", "v1", credentials=creds)

        message = service.users().messages().get(
            userId="me",
            id=message_id,
            format="full"
        ).execute()

        return message

    def parse_message_payload(self, msg):
        headers = msg.get("payload", {}).get("headers", [])
        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "")
        sender = next((h["value"] for h in headers if h["name"] == "From"), "")

        body = ""
        payload = msg.get("payload", {})

        # parsing email normally
        if "parts" in payload:
            for part in payload["parts"]:
                if part.get("mimeType") == "text/plain":
                    body_data = part["body"].get("data", "")
                    body = base64.urlsafe_b64decode(body_data.encode()).decode("utf-8", errors="ignore")
                    break
        else:
            body_data = payload.get("body", {}).get("data", "")
            if body_data:
                body = base64.urlsafe_b64decode(body_data.encode()).decode("utf-8", errors="ignore")

        return {
            "subject": subject,
            "sender": sender,
            "body": body
        }

    def check_unread_emails(self, user):
        creds = build_credentials_for_user(user)
        service = build("gmail", "v1", credentials=creds)

        query_inbox_messages = service.users().messages().list(
            userId="me",
            labelIds=["INBOX"],
            q="is:unread"
        ).execute()

        return query_inbox_messages.get("messages") or []

    # TODO: this should be broken into smaller functions
    def poll_emails(self, user_id):
        with self.app.app_context():
            user = self.__repository.get_user_by_id(user_id)
            # TODO: raise exception if user is not found + log
            while True:
                logger.info("[{}] Checking for unread emails for user {}...".format(threading.get_native_id(),
                                                                                 user.user_email))
                unread_messages = self.check_unread_emails(user)
                if unread_messages:
                    is_seen_email = False
                    for msg_meta in unread_messages:
                        msg = self.fetch_email_content(user, msg_meta["id"])

                        # Check if the msg has already been seen by the poller service
                        if self.__repository.is_email_processed(msg_meta["id"]):
                            continue
                        parsed = self.parse_message_payload(msg)
                        parsed_email = Email(
                            user_id=user.user_id,
                            gmail_message_id=msg_meta["id"],
                            email_subject=parsed["subject"],
                            email_sender=parsed["sender"],
                            email_body=parsed["body"],
                            email_recipient=user.user_email
                        )
                        self.__repository.save_email(parsed_email)
                        logger.info("[{}] New email received: {}".format(threading.get_native_id(),parsed_email))
                        is_seen_email = True
                        response = requests.post("http://localhost:5000/emails/predict_email",
                                                 json={"email_id": parsed_email.email_id})
                        if response.status_code == 200:
                            logger.info(f"[{threading.get_native_id()}] Classification result: {response.json()}")
                        else:
                            logger.warning(f"[{threading.get_native_id()}] Classification failed: {response.text}")

                    if not is_seen_email:
                        logger.info("[{}] No new emails found for user {}!".format(threading.get_native_id(),
                                                                                    user.user_email))
                else:
                    logger.info("[{}] User {} has no incoming messages".format(threading.get_native_id(),
                                                                               user.user_email))
                time.sleep(POLLING_INTERVAL)
