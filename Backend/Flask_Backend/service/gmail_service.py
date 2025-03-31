from flask import current_app

from database import db
from repository.repository import Repository
from service.poller_service import PollerService
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
        poller = PollerService(current_app._get_current_object(), db.session)
        poller.start_polling(user.user_id)