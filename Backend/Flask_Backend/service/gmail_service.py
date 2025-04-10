from flask import current_app
from google_auth_oauthlib import get_user_credentials

from database import db
from repository.repository import Repository
from service.poller_service import PollerService
from utils import email_utils
from utils.email_utils import build_credentials_for_user
from utils.logs import get_logger
from googleapiclient.discovery import build

logger = get_logger()


class GmailService:
    def __init__(self, db_session):
        self.__repository = Repository(db_session)

    def fetch_inbox(self, user):
        token = self.__repository.get_token_by_user(user)
        creds = build_credentials_for_user(token)
        try:
            service = build('gmail', 'v1', credentials=creds, num_retries=5)
        except:
            pass

    def handle_oauth_callback(self, creds, user):
        self.__repository.save_token(creds, user)
#        poller = PollerService(current_app._get_current_object(), db.session)
#        poller.start_polling(user.user_id)

    """
    Will process the push notification by extracting the whole email content from the history id
    """
    def process_notification(self, email_address, history_id):
        creds = email_utils.get_credentials_for_user(email_address)

        service = build("gmail", "v1", credentials=creds)
        # Retrieval of the email we want to process
        gmail_history = service.users().history().list(
            userId='me',
            maxResults=1,
            startHistoryId=str(int(history_id) - 1),
        ).execute()

        for record in gmail_history.get('history', []):
            for msg in record.get('messagesAdded', []):
                msg_id = msg['message']['id']
                full_msg = service.users().messages().get(
                    userId='me',
                    id=msg_id,
                    format='full'
                ).execute()
                logger.info("The full message is: {}".format(full_msg))