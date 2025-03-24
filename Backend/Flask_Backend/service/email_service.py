from repository.repository import Repository
from utils.email_utils import get_email_header, load_model, get_email_body
from utils.logs import get_logger

logger = get_logger()

class EmailService:
    def __init__(self, db_session):
        self.__repository = Repository(db_session)
        self.__model = load_model()

    def handle_email(self, email):
        headers = get_email_header(email)

        # Extract relevant header information
        sender = headers.get("From", "Unknown")
        recipient = headers.get("To", "Unknown")
        subject = headers.get("Subject", "Subject not found")

        email = self.__repository.save_email(email)
        return email

    def predict_email_text(self, email):
        email_body = get_email_body(email)
        predicted_value = self.__model.predict_proba([email_body])
        logger.info("Phishing email percent: {}\n Safe email percent: {}").format(predicted_value)