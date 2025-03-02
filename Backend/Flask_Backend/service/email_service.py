from repository.repository import Repository
from utils.email_utils import get_email_header


class EmailService:
    def __init__(self, db_session):
        self.__repository = Repository(db_session)

    def handle_email(self, email):
        headers = get_email_header(email)

        # Extract relevant header information
        sender = headers.get("From", "Unknown")
        recipient = headers.get("To", "Unknown")
        subject = headers.get("Subject", "Subject not found")

        email = self.__repository.save_email(email)
        return email